/**********************************************************************
Finds the 100 best features in an image, and tracks these
features to the next image.  Saves the feature
locations (before and after tracking) to text files and to PPM files,
and prints the features to the screen.
**********************************************************************/

#include "pnmio.h"
#include "klt.h"
#include <stdlib.h>

#ifdef WIN32
int RunExample1()
#else
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
int main(int argc, char *argv[])

/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
#endif
{

  if (argc != 28)
  {
    printf("ERROR, no están todas las variables necesarias cargadas :(\n");
    return -1;
  }
  else{
    printf("\n----------------------------- \n----------------------------- \n----------------------------- ESTÁN TODAS LAS VARIABLES CARGADAS :) \n----------------------------- \n----------------------------- \n----------------------------- ");
  }
  

  unsigned char *img1, *img2;
  KLT_TrackingContext tc;
  KLT_FeatureList fl;
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
  int nFeatures = atoi(argv[1]);
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/

  int ncols, nrows;
  int i;

/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
  tc = KLTCreateTrackingContext(
    atoi(argv[4]),  //int mindist
    atoi(argv[5]),  //int window_size
    atoi(argv[6]),  //KLT_BOOL sequentialMode
    atoi(argv[7]),  //KLT_BOOL smoothBeforeSelecting
    atoi(argv[8]),  //KLT_BOOL writeInternalImages
    atoi(argv[9]),  //KLT_BOOL lighting_insensitive
    atoi(argv[10]), //int min_eigenvalue
    atof(argv[11]), //float min_determinant
    atof(argv[12]), //float max_iterations
    atof(argv[13]), //float min_displacement
    atof(argv[14]), //float max_residue
    atof(argv[15]), //float grad_sigma
    atof(argv[16]), //float smooth_sigma_fact
    atof(argv[17]), //float pyramid_sigma_fact
    atof(argv[18]), //float step_factor
    atoi(argv[19]), //int nSkippedPixels
    atoi(argv[20]), //int affineConsistencyCheck
    atoi(argv[21]), //int affine_window_size
    atoi(argv[22]), //int affine_max_iterations
    atof(argv[23]), //float affine_max_residue
    atof(argv[24]), //float affine_min_displacement
    atof(argv[25]), //float affine_max_displacement_differ
    atoi(argv[26])  //int search_range
  );
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/

  KLTPrintTrackingContext(tc);
  fl = KLTCreateFeatureList(nFeatures);
  
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
  img1 = pgmReadFile(argv[2], NULL, &ncols, &nrows);
  img2 = pgmReadFile(argv[3], NULL, &ncols, &nrows);
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/

  KLTSelectGoodFeatures(tc, img1, ncols, nrows, fl);



/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
  float *x1 = (float *)malloc(fl->nFeatures * sizeof(float));
  float *y1 = (float *)malloc(fl->nFeatures * sizeof(float));
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/

  

  printf("\nIn first image:\n");
  for (i = 0 ; i < fl->nFeatures ; i++)  {

/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
    x1[i] = fl->feature[i]->x;
    y1[i] = fl->feature[i]->y;
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/


    printf("Feature #%d:  (%f,%f) with value of %d\n",
           i, fl->feature[i]->x, fl->feature[i]->y,
           fl->feature[i]->val);
  }

  KLTWriteFeatureListToPPM(fl, img1, ncols, nrows, "KLT_feat1.ppm");
  KLTWriteFeatureList(fl, "KLT_feat1.txt", "%3d");

  KLTTrackFeatures(tc, img1, img2, ncols, nrows, fl);

/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
  int contador = atoi(argv[27]);
  char nombre_archivo[300]; 
  sprintf(nombre_archivo, "%d_KLT_openpiv.vec", contador);

  FILE *f = fopen(nombre_archivo, "w");
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/

  printf("\nIn second image:\n");
  for (i = 0 ; i < fl->nFeatures ; i++)  {



/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
    float x2 = fl->feature[i]->x;
    float y2 = fl->feature[i]->y;
    int v2 = fl->feature[i]->val;

    float x = x1[i];
    float y = y1[i];

    float u = x2 - x1[i];
    float v = y2 - y1[i];
    float mask = 0.0f;  //Por defecto, el vector es válido

    if(v2 < 0){
      mask = 1.0f; // Si el valor final es negativo (en la segunda imagen, después de haber calculado ambas), el vector es inválido
    }

    
    float sig2noise = 0.0f;

    fprintf(f, "%8.4f\t%8.4f\t%8.4f\t%8.4f\t%8.4f\t%8.4f\n",
            x, y, -u, v, mask, sig2noise);


 /*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/


    printf("Feature #%d:  (%f,%f) with value of %d\n",
           i, fl->feature[i]->x, fl->feature[i]->y,
           fl->feature[i]->val);
  }

  KLTWriteFeatureListToPPM(fl, img2, ncols, nrows, "KLT_feat2.ppm");
  KLTWriteFeatureList(fl, "KLT_feat2.fl", NULL);      /* binary file */
  KLTWriteFeatureList(fl, "KLT_feat2.txt", "%5.1f");  /* text file   */


/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
/*------------------------- CONTRIBUCION -------------------------*/
  fclose(f);
  free(x1);
  free(y1);
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/
/*------------------------- FIN DE LA CONTRIBUCION -------------------------*/


  return 0;
}

