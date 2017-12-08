
#include <_fake_defines.h>
#include <_fake_typedefs.h>

#define RowDim 20
#define ColDim 20
#define Generations 20

#define MOD(a,b) ((((a)%(b))+(b))%(b))

struct Neighborhood
{
    
    bool left;
    
    bool right;
    
    bool up;
    
    bool down;
    
};

void initialize(bool * matrix)
{
    for (int i=0; i<(RowDim*ColDim); ++i)
    {
        matrix[i] = 0;
    }

    /* x = i * coldim + j */
    matrix[10*ColDim+10] = 1;
    matrix[10*ColDim+11] = 1;
    matrix[10*ColDim+12] = 1;
    matrix[11*ColDim+11] = 1;
    // matrix[9*ColDim+11] = 1;
}

bool function(struct Neighborhood nbhd)
{
    /* Defined Neighborhood
    nbhd.left [1, 1]; nbhd.right [-1, -1]; nbhd.up [-1, 1]; nbhd.down [1, 1];     
    */ 

    // int sum = nbhd.c0 + nbhd.c2 + nbhd.c3 + nbhd.c4 + nbhd.c5 + nbhd.c6 + nbhd.c7 + nbhd.c8;
    // int site = nbhd.c1;
    // return ( site == 1 ) ? ( sum == 2 || sum == 3 ) ? 1:0 : ( sum == 3 ) ? 1:0;

    return 0;
}

struct Neighborhood neighborhood(const bool * matrix, int i)
{
    struct Neighborhood nbhd;

    int row = i / ColDim;
    int col = MOD(i,ColDim);

    
    nbhd.left = matrix[ MOD(row + (1),RowDim)*ColDim + MOD(col + (1),ColDim) ];
    
    nbhd.right = matrix[ MOD(row + (-1),RowDim)*ColDim + MOD(col + (-1),ColDim) ];
    
    nbhd.up = matrix[ MOD(row + (-1),RowDim)*ColDim + MOD(col + (1),ColDim) ];
    
    nbhd.down = matrix[ MOD(row + (1),RowDim)*ColDim + MOD(col + (1),ColDim) ];
    

    return nbhd;
}

void evolve(bool * in, bool * out)
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

int main(int argc, char const **argv)
{

    bool * in = (bool *) malloc(RowDim*ColDim*sizeof( bool ));
    bool * out = (bool *) malloc(RowDim*ColDim*sizeof( bool ));

    initialize(in);
    initialize(out);
    evolve(in,out);

    /* -- Releasing resources -- */
    free(in);
    free(out);

    return EXIT_SUCCESS;
}

