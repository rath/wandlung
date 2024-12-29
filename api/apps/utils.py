
def srt_to_webvtt(srt_content: str) -> str:
    """
    Convert the given SRT content to WebVTT format and return as a string.
    """
    blocks = srt_content.strip().split('\n\n')
    vtt_lines = ['WEBVTT', '']  # Start with WEBVTT header and a blank line

    for block in blocks:
        lines = block.split('\n')

        # SRT block typically has:
        #   1                 (subtitle number)
        #   00:00:01,000 --> 00:00:04,000
        #   Subtitle text line 1
        #   Subtitle text line 2 (optional)
        if len(lines) < 2:
            continue  # skip if block doesn't have enough lines

        # The second line is the time range, convert commas to periods
        time_line = lines[1].replace(',', '.')

        # The rest of the lines are subtitle text
        text_lines = lines[2:]

        vtt_lines.append(time_line)
        vtt_lines.extend(text_lines)
        vtt_lines.append('')  # blank line between cues in VTT

    # Join everything with newlines
    return '\n'.join(vtt_lines)

