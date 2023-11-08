import argparse

from simple_sentence_segment import sentence_segment


def break_sentence(s, seg_len):
    segments = []
    points = list(range(0, len(s), seg_len))
    if points[-1] != len(s): points.append(len(s))
    for i in range(len(points) - 1):
        segments.append(s[points[i]:points[i + 1]])
    return segments


def process(text, seg_len):

    # get sentences
    init_sentences = list()
    for s, t in sentence_segment(text):
        init_sentences.append(text[s:t])

    # break large sentences
    sentences = list()
    for i, s in enumerate(init_sentences):
        if len(s) > seg_len:
            sentences += break_sentence(s, seg_len)
        else:
            sentences.append(s)

    # create segments
    segments = []
    segment = ""
    # add sentences until adding the next one makes the segment too long
    # then store the segment and start with a new one
    for s in sentences:
        if len(segment) + len(s) > seg_len:
            segments.append(segment)
            segment = ""
        segment = segment + s
    segments.append(segment)
    return segments


def segmentation(text):
    parser = argparse.ArgumentParser()

    parser.add_argument('--segment_length',
                        default=20000,
                        type=int)

    args = parser.parse_args()
    return process(text, args.segment_length)




