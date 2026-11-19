"""Time the Ising Gibbs sampler and Algorithm 1 seed readout at several image sizes.

Synthetic test only: a bright noisy disk on a dark noisy background, so the
true mask is known. Uses the sign-compatible convention
Delta=atan(alpha*(tau-d)), H=-sum Delta*Z_i*Z_j/4, b=4K/median|Delta|, with the
EMNIST settings tau=100, alpha=0.001, K=0.8. No spin is pinned; the seed is the
disk centre and only labels the readout C(F,i)>0. This is a scaling check, not
segmentation evidence (handoff page 7: thresholding masks are easy by design).

Writes results.json and sizes.png to --output. Does not touch any study folder.
"""
import argparse
import json
import os
import time
from pathlib import Path

os.environ.setdefault('NUMBA_CACHE_DIR', str(Path(os.environ.get('TEMP', '/tmp'))/'qs-numba'))
import numpy as np
from ising_monte_carlo import sample_gibbs, signed_image

TAU, ALPHA, K = 100., .001, .8


def disk_image(side, noise, rng):
    y, x = np.mgrid[:side, :side]
    c = (side-1)/2
    truth = (x-c)**2+(y-c)**2 <= (side/3)**2
    image = np.where(truth, 200., 50.)+rng.normal(0, noise, (side, side))
    return np.clip(image, 0, 255), truth


def run_size(side, noise, burn, samples, chains, rng_seed):
    image, truth = disk_image(side, noise, np.random.default_rng(rng_seed))
    model = signed_image(image, ALPHA, threshold=TAU)
    b = 4*K/float(np.median(abs(model.delta)))
    seed = (side//2)*side+side//2
    start = time.perf_counter()
    r = sample_gibbs(model, [b], seeds=[seed], burn=burn, samples=samples,
                     block_size=64, chains=chains, rng_seed=rng_seed)
    seconds = time.perf_counter()-start
    gamma, se = r['gamma'][0, 0], r['se'][0, 0]
    pred = gamma > 0
    t = truth.ravel()
    iou = float((pred & t).sum()/max((pred | t).sum(), 1))
    resolved = np.abs(gamma) > 1.96*se
    rows, cols = np.divmod(np.arange(model.n), side)
    distance = np.hypot(rows-side//2, cols-side//2)
    return dict(side=side, n=model.n, b=b, beta_paper=b*model.n, seconds=seconds,
                iou=iou, unresolved=float(1-resolved.mean()),
                rhat_max=float(np.nanmax(r['rhat_gamma'])),
                negative_edges=int((model.delta < 0).sum()),
                gamma=gamma.tolist(), distance=distance.tolist(),
                truth=t.astype(int).tolist(), image=image.ravel().tolist())


def plot(results, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors = ['#2a78d6', '#e07b39', '#2e9e6b', '#b5479a', '#7a6fd0', '#c9a227']
    fig = plt.figure(figsize=(13, 7.5), layout='constrained')
    grid = fig.add_gridspec(2, max(3, len(results)))
    ax_t, ax_q, ax_g = (fig.add_subplot(grid[0, i]) for i in range(3))
    for res, color in zip(results, colors):
        label = f"{res['side']}×{res['side']}"
        ax_t.plot(res['n'], res['seconds'], 'o', color=color, ms=9, label=label)
        ax_q.bar(label, res['iou'], color=color)
        truth = np.array(res['truth'], bool)
        d, g = np.array(res['distance']), np.array(res['gamma'])
        ax_g.scatter(d[truth]/res['side'], g[truth], s=8, color=color, alpha=.6, label=label)
        ax_g.scatter(d[~truth]/res['side'], g[~truth], s=8, color=color, alpha=.6, marker='x')
    ns = [r['n'] for r in results]
    ax_t.plot(ns, [r['seconds'] for r in results], color='#888', lw=1, zorder=0)
    ax_t.set(xscale='log', yscale='log', xlabel='pixels N (log)', ylabel='sampler time, s (log)',
             title='Runtime vs size')
    ax_t.legend(frameon=False)
    ax_q.set(ylim=(0, 1.05), ylabel='IoU (seed sign rule)', title='Segmentation vs truth')
    for i, r in enumerate(results):
        ax_q.text(i, r['iou']+.02, f"{r['iou']:.3f}", ha='center')
    ax_g.axhline(0, color='#888', lw=1)
    ax_g.set(xlabel='distance from seed / image side', ylabel='Γ(seed, i)',
             title='Seed correlations (● disk, × background)')
    ax_g.legend(frameon=False, markerscale=2)
    for i, (res, color) in enumerate(zip(results, colors)):
        ax = fig.add_subplot(grid[1, i])
        side = res['side']
        ax.imshow(np.array(res['gamma']).reshape(side, side), cmap='RdBu_r', vmin=-.25, vmax=.25)
        ax.contour(np.array(res['truth']).reshape(side, side), levels=[.5], colors='k', linewidths=.8)
        ax.set_title(f"{side}×{side}: Γ map, IoU {res['iou']:.3f}", color=color)
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle('Ising Gibbs sampler and Algorithm 1 seed readout at different image sizes '
                 f'(τ={TAU:g}, α={ALPHA:g}, K={K:g})')
    fig.savefig(path, dpi=150)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--sizes', type=int, nargs='+', default=[8, 16, 32, 64])
    parser.add_argument('--noise', type=float, default=30., help='Gaussian intensity noise SD')
    parser.add_argument('--burn', type=int, default=512)
    parser.add_argument('--samples', type=int, default=1024)
    parser.add_argument('--chains', type=int, default=2)
    parser.add_argument('--rng-seed', type=int, default=20261110)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1]/'results'/'student-scaling')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    # Compile numba kernels on a tiny image so the first size's timing is fair.
    run_size(4, args.noise, 64, 256, 2, 0)
    results = []
    for side in args.sizes:
        res = run_size(side, args.noise, args.burn, args.samples, args.chains, args.rng_seed)
        print(f"{side:>3}x{side:<3} N={res['n']:>5}  {res['seconds']:8.1f} s  IoU {res['iou']:.3f}  "
              f"unresolved {res['unresolved']:.1%}  max R-hat {res['rhat_max']:.3f}", flush=True)
        results.append(res)
    settings = {k: v for k, v in vars(args).items() if k != 'output'}
    (args.output/'results.json').write_text(json.dumps(
        dict(settings=settings, tau=TAU, alpha=ALPHA, K=K, results=results), indent=1)+'\n')
    plot(results, args.output/'sizes.png')
    print('wrote', args.output/'sizes.png')


if __name__ == '__main__':
    main()
