import argparse
import pygame
import sys
from blobs.blob import Blob
from communities.community import Community
import random

# Visual parameters
def initialize_window(grid_size, scale=10):
    pygame.init()
    size = grid_size * scale
    screen = pygame.display.set_mode((size, size))
    pygame.display.set_caption("BlobSociety")
    return screen, scale

def assign_colors_to_communities(communities):
    color_map = {}
    palette = [
        (255, 0, 0),     # Red
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (255, 255, 0),   # Yellow
        (255, 165, 0),   # Orange
        (128, 0, 128),   # Purple
        (0, 255, 255),   # Cyan
    ]
    for i, community in enumerate(communities):
        color_map[community.name] = palette[i % len(palette)]
    return color_map

def draw_world(screen, blobs, communities, scale, grid_size):
    screen.fill((30, 30, 30))
    colors = assign_colors_to_communities(communities)
    for blob in blobs:
        x = int(blob.position[0] * scale)
        y = int(blob.position[1] * scale)
        color = (200, 200, 200)  # default gray
        if blob.community:
            color = colors.get(blob.community.name, color)
        pygame.draw.circle(screen, color, (x, y), max(2, scale // 2))
    pygame.display.flip()


def parse_args():
    parser = argparse.ArgumentParser(description="BlobSociety Simulation")
    parser.add_argument('--num-blobs', type=int, default=20)
    parser.add_argument('--grid-size', type=int, default=50)
    return parser.parse_args()


def initialize_blobs(n, grid_size, movement_unit=5):
    return [
        Blob(
            i,
            (random.uniform(0, grid_size), random.uniform(0, grid_size)),
            movement_unit,
            grid_size
        )
        for i in range(n)
    ]



def initialize_communities():
    return [
        Community("Kinbound", ['loyalty','strength','resilience']),
        Community("Harmonia", ['empathy','curiosity','charisma']),
        Community("Bastion", ['strength','loyalty']),
        Community("Flux", ['intelligence','charisma','curiosity']),
    ]


def main():
    args = parse_args()
    blobs = initialize_blobs(args.num_blobs, args.grid_size)
    communities = initialize_communities()
    screen, scale = initialize_window(args.grid_size)
    day = 0

    print(f"Initialized {len(blobs)} blobs on a {args.grid_size}x{args.grid_size} grid.")
    draw_world(screen, blobs, communities, scale, args.grid_size)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Closing window.")
                pygame.quit()
                sys.exit()

        cmd = input("Enter command (day/new/quit): ").strip().lower()
        if cmd == 'day':
            day += 1
            print(f"\n-- Day {day} --")
            for blob in blobs:
                blob.decide_move(blobs)
                print(f"Blob {blob.id} moved to {blob.position}")
                blob.act({'blobs': blobs})
            for c in communities:
                c.evaluate_leadership()
                c.evolve()
            draw_world(screen, blobs, communities, scale, args.grid_size)
        elif cmd == 'new':
            new_blob = Blob(len(blobs), (args.grid_size // 2, args.grid_size // 2), grid_size=args.grid_size)
            new_blob.evaluate_community(communities)
            blobs.append(new_blob)
            print(f"Generated Blob {new_blob.id} at center with traits {new_blob.traits}")
            draw_world(screen, blobs, communities, scale, args.grid_size)
        elif cmd == 'quit':
            print("Exiting simulation.")
            pygame.quit()
            break
        else:
            print("Unknown command. Use day, new, or quit.")

if __name__ == '__main__':
    main()
