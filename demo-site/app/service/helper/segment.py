import argparse


def break_text(text, max_length):
    segments = []
    current_segment = ""
    for sentence in text.split('. '):  # Split text into sentences
        if len(current_segment) + len(sentence) <= max_length:
            current_segment += sentence + '. '  # Add the sentence to the current segment
        else:
            segments.append(current_segment)  # Store the current segment
            current_segment = sentence + '. '  # Start a new segment with the sentence

    if current_segment:
        segments.append(current_segment)  # Add the last segment if not empty

    return segments


def process(text, seg_len):
    segments = break_text(text, seg_len)
    return segments


def segmentation(text):
    parser = argparse.ArgumentParser()

    parser.add_argument('--segment_length',
                        default=20000,
                        type=int)

    args = parser.parse_args()
    return process(text, args.segment_length)
