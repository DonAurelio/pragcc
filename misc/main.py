# -*- encoding: utf-8 -*-

def insert_lines(raw,insertions=[]):
    lines = raw.splitlines()
    numbered_lines = list(enumerate(lines))
    fake_line = -1

    new_numbered_lines = []
    for new_raw, insertion_line in insertions:
        for list_index, code in enumerate(numbered_lines):
            line_in_code = code[0]
            if line_in_code is insertion_line:
                new_numbered_lines += numbered_lines[:list_index]
                new_numbered_lines += [(fake_line,new_raw)]
                new_numbered_lines += numbered_lines[list_index:]

        numbered_lines = new_numbered_lines
        new_numbered_lines = []

    return '\n'.join([code[1] for code in numbered_lines])
    # return numbered_lines



if __name__ == '__main__':
    raw = \
"""void evolve(bool * in, bool * out)
{
    struct Neighborhood nbhd;
    bool * temp = in;

    for (int i = 1; i <= Generations; ++i)
    {
        for (int i = 0; i < (RowDim*ColDim); ++i)
        {
            nbhd = neighborhood(in,i);
            out[i] = function(nbhd);
        }

        temp = in;
        in = out;
        out = temp;
    }
}
"""
    insertions = [('Insertion 5',5),('Insertion 7',7)]
    raw = insert_lines(raw,insertions)

    print(raw)