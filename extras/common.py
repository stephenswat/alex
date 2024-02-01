import re


def parse_filename(s: str):
    if m := re.fullmatch(
        r"([A-Za-z0-9]+)-(\d+(?:_\d+)*)-(\d+)-([A-Za-z0-9_\-]+)-(?:log|ranking).csv", s
    ):
        return (m.group(1), m.group(2), m.group(3), m.group(4))
    else:
        raise ValueError("Invalid file name " + s + "!")


def render_pattern(ptrn: str, tex: bool = True):
    splt = ptrn.split("_")

    if splt[0] in ["Cholesky", "Crout"] or splt[0][:2] == "MM":
        if splt[0][:3] == "MMT":
            rem = str(splt[1]) + ", " + str(splt[1])
        else:
            rem = str(splt[1])
    else:
        rem = ", ".join(str(i) for i in splt[1:])

    return f"$\\textsc{{{splt[0]}}}({rem}; 4)$" if tex else f"{splt[0]}({rem}; 4)"
