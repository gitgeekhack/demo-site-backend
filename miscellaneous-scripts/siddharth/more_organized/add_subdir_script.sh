#!/bin/bash

# Iterate over all subdirectories in the current directory
for dir in */; do
  # Create a new subdirectory within each subdirectory
  mkdir -p "$dir/splitted"

  # Move the contents of the subdirectory into the new subdirectory
  mv "$dir"/* "$dir/splitted/"
done
