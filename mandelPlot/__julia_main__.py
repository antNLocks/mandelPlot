"""Main call to julia. Mostly a parser."""
import argparse
from mandelPlot.julia import plot_julia


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Build and save an image of a Julia set')
    parser.add_argument('-c', metavar='c', type=complex,
                        help='complex value defining this Julia set', default=(-0.8 + 0.156j))

    parser.add_argument('--box','-b', metavar='box', type=tuple,
                        help='box bounds', default=(-2-2j, 2+2j))

    parser.add_argument('--width_pixel_number','-w', metavar='width_pixel_number', type=int,
                        help='number of pixels of the width of the image', default=2000)

    parser.add_argument('--max_iter','-m', metavar='max_iter', type=int,
                        help='max iterations - precision indicator', default=50)

    parser.add_argument('--fig_path','-f', metavar='fig_path', type=str,
                        help='path of the resulting image', default="./julia_graph.png")
                        
    args = parser.parse_args()

    plot_julia(args.c, args.box[0], args.box[1], args.width_pixel_number, args.max_iter, args.fig_path)

if __name__=="__main__":
    main()