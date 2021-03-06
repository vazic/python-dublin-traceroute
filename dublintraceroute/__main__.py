from __future__ import absolute_import
from __future__ import print_function

import json

from .dublintraceroute import (
    DublinTraceroute,
    to_graphviz,
    _dublintraceroute,
)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # subparser for the `plot` command
    plot_parser = subparsers.add_parser(
        'plot',
        help='Plot a traceroute from JSON results',
    )
    plot_parser.add_argument(
        'jsonfile', type=argparse.FileType('r'),
        help='The input JSON file generated by dublin-traceroute',
    )

    # subparser for the `trace` command
    traceroute_parser = subparsers.add_parser(
        'trace', help='Run a multipath traceroute towards a target',
    )
    traceroute_parser.add_argument(
        'target',
        help='The target IP or hostname')
    traceroute_parser.add_argument(
        '-s', '--sport', type=int,
        default=_dublintraceroute.DEFAULT_SPORT,
        help='The source port for the probes (default: {s})'.format(
            s=_dublintraceroute.DEFAULT_SPORT,
        ),
    )
    traceroute_parser.add_argument(
        '-d', '--dport', type=int,
        default=_dublintraceroute.DEFAULT_DPORT,
        help='The base destination port for the probes (default: {d})'.format(
            d=_dublintraceroute.DEFAULT_DPORT,
        ),
    )
    traceroute_parser.add_argument(
        '-n', '--npaths', type=int,
        default=_dublintraceroute.DEFAULT_NPATHS,
        help='The number of network paths to probe (default: {n})'.format(
            n=_dublintraceroute.DEFAULT_NPATHS,
        ),
    )
    traceroute_parser.add_argument(
        '-t', '--min-ttl', type=int,
        default=_dublintraceroute.DEFAULT_MIN_TTL,
        help='The minimum TTL to reach (default: {t})'.format(
            t=_dublintraceroute.DEFAULT_MIN_TTL,
        ),
    )
    traceroute_parser.add_argument(
        '-T', '--max-ttl', type=int,
        default=_dublintraceroute.DEFAULT_MAX_TTL,
        help='The maximum TTL to reach (default: {t})'.format(
            t=_dublintraceroute.DEFAULT_MAX_TTL,
        ),
    )
    traceroute_parser.add_argument(
        '-D', '--delay', type=int,
        default=_dublintraceroute.DEFAULT_DELAY,
        help='The inter-packet delay (default: {d})'.format(
            d=_dublintraceroute.DEFAULT_DELAY,
        ),
    )
    traceroute_parser.add_argument(
        '-b', '--broken-nat', action='store_true',
        default=bool(_dublintraceroute.DEFAULT_BROKEN_NAT),
        help=('The network has a broken NAT (e.g. no payload fixup). Try this '
              'if you see less hops than expected (default: {b})'.format(
                  b=bool(_dublintraceroute.DEFAULT_BROKEN_NAT),
                  )),
    )
    traceroute_parser.add_argument(
        '-j', '--json', action='store_true', default=False,
        help='Save results to traceroute_<target>.json',
    )
    traceroute_parser.add_argument(
        '-p', '--plot', action='store_true', default=False,
        help='Plot results to traceroute_<target>.png',
    )

    return parser.parse_args()


def plot(results, outfile):
        graph = to_graphviz(results)
        graph.layout('dot')
        graph.draw(outfile)
        print('Saved to {outfile}'.format(outfile=outfile))


def save_json(results, outfile):
    with open(outfile, 'w') as fd:
        json.dump(results, fd, indent=2)
        print('Saved to {outfile}'.format(outfile=outfile))


def main():
    args = parse_args()
    if args.command == 'trace':
        print('Traceroute to {t}'.format(t=args.target))
        print('  Source port: {s}, destination port: {d}, num paths: {n}, '
              'min TTL: {mint}, max TTL: {maxt}, delay: {delay}, '
              'broken NAT: {bn}'.format(
                  s=args.sport,
                  d=args.dport,
                  n=args.npaths,
                  mint=args.min_ttl,
                  maxt=args.max_ttl,
                  delay=args.delay,
                  bn=args.broken_nat,
              ))
        dub = DublinTraceroute(args.target, args.sport, args.dport, args.npaths,
                               args.min_ttl, args.max_ttl, args.delay,
                               args.broken_nat)
        results = dub.traceroute()
        results.pretty_print()

        if args.plot:
            plot(results, 'traceroute_{target}.png'.format(target=args.target))

        if args.json:
            save_json(
                results,
                'traceroute_{target}.json'.format(target=args.target),
            )

    elif args.command == 'plot':
        results = json.load(args.jsonfile)
        outfile = args.jsonfile.name + '.png'
        plot(results, outfile)

    else:
        print('No action requested. Try --help')

main()
