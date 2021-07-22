import sys
from butch.context import Context


def percent_expansion(line: str, ctx: Context) -> str:
    "Expand percent-encapsulated values into variables."
    # pylint: disable=too-many-statements, too-many-branches
    tmp = ""
    idx = 0
    line_len = len(line)
    while idx < line_len:
        char = line[idx]
        if char != "%":
            tmp += char
            idx += 1
            continue

        if line_len == 1:
            break

        next_perc = line.find("%", idx + 1)
        # %%
        if idx == next_perc:
            if idx + 1 != line_len:
                tmp += "%"
            idx += 1
            continue

        next_idx = idx + 1
        # sys argv
        # %1hello% -> <argv>hello instead of <1hello value>
        if idx < line_len - 1:
            next_char = line[next_idx]
            if next_char.isdigit():
                pos = int(line[next_idx])
                val = sys.argv[pos:pos + 1]
                # value or position/number
                tmp += val[0] if val else str(pos)
                idx = next_idx + 1
                continue

            if next_char == "*":
                tmp += " ".join(sys.argv[1:10])
                idx = next_idx + 1
                continue

            if next_char == "%":
                tmp += next_char
                idx = next_idx + 1
                continue

        if next_perc < 0:
            idx += 1
            continue

        # variable expansion
        idx_ahead = next_perc + 1
        perc_range = next_perc - idx
        if next_perc and perc_range > 1 and " " not in line[idx:idx_ahead]:
            tmp += ctx.get_variable(key=line[next_idx:next_perc])
            idx = idx_ahead
            continue

        # escaped %, as %% -> %
        if next_perc and perc_range == 1:
            tmp += "%"
            idx = idx_ahead
            continue
        if next_perc and not perc_range:
            idx += 1
            if idx != line_len:
                tmp += "%"
            continue
    ctx.log.debug("percent expansion result: %r", tmp)
    return tmp
