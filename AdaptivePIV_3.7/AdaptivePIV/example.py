import numpy as np
import PIV
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
import openpiv.tools as piv_tls
import sys
import ast

        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================

        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================

def experimental_example(counter, imageA = None, imageB = None ,im_number=1, settings=None):
    """Demonstrates the PIV algorithm on an actual image from an experiment
    The experiment is the flow over a backwards facing step.
    """

    if imageA is not None and imageB is not None:
        img = PIV.piv_image.PIVImage(imageA, imageB)

    else:
        # load a PIV image
        img = PIV.piv_image.PIVImage.from_flowtype(flowtype=1, im_number=im_number)

        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================


    # show the images
    #img.plot_images_animation()

    # define settings if not passed in
    if settings is None:
        settings = PIV.analysis.WidimSettings(init_WS=97,
                                              final_WS=33,
                                              WOR=0.5,
                                              n_iter_main=3,
                                              n_iter_ref=1,
                                              vec_val='NMT',
                                              interp='struc_cub')
        
    
    #======================================================CONTRIBUCIÓN==========================================================
    #======================================================CONTRIBUCIÓN==========================================================
    #======================================================CONTRIBUCIÓN==========================================================
    #======================================================CONTRIBUCIÓN==========================================================
    #======================================================CONTRIBUCIÓN==========================================================

    # analyse the image
    disp_field = PIV.analysis.widim(counter, img, settings)
    #

    #==============================================FIN DE LA CONTRIBUCIÓN========================================================
    #==============================================FIN DE LA CONTRIBUCIÓN========================================================
    #==============================================FIN DE LA CONTRIBUCIÓN========================================================
    #==============================================FIN DE LA CONTRIBUCIÓN========================================================
    #==============================================FIN DE LA CONTRIBUCIÓN========================================================

    # plot displacement field
    disp_field.plot_displacement_field(width=0.001, minshaft=2)
    #plt.show()

def synthetic_example(dim=(500, 500), settings=None):
    """Demonstrates the ability to generate synthetic images with arbitrary
    displacement fields, and then analyses the images.
    """

    # define flow field
    u, v = np.empty(dim), np.empty(dim)
    xx, yy = np.meshgrid(np.arange(dim[1]), np.arange(dim[0]))

    u = 15 * (np.cos((xx * 2*np.pi)/dim[1] + (np.pi / 2)) *
              np.cos((yy * 2 * np.pi)/dim[0]))
    v = 15 * (np.sin((xx * 2*np.pi)/dim[1] + (np.pi / 2)) *
              np.sin((yy * 2 * np.pi)/dim[0]))

    # create synthetic images
    ima, imb = PIV.piv_image.create_synthetic_image_pair(dim, seed_dens=0.035,
                                                         u=u, v=v)

    # create and show images
    img = PIV.piv_image.PIVImage(ima, imb)
    img.plot_images_animation()

    if settings is None:
        settings = PIV.analysis.WidimSettings(init_WS=97,
                                              final_WS=33,
                                              WOR=0.5,
                                              n_iter_main=3,
                                              n_iter_ref=1,
                                              vec_val='NMT',
                                              interp='struc_cub')

    # analyse the image
    disp_field = PIV.analysis.widim(img, settings)


    # plot displacement field
    disp_field.plot_displacement_field(width=0.001, minshaft=2)
    plt.show()


if __name__ == "__main__":


        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================

    init_WS = int(sys.argv[1])
    final_WS = int(sys.argv[2])
    WOR = float(sys.argv[3])
    n_iter_main = int(sys.argv[4])
    n_iter_ref = int(sys.argv[5])
    vec_val = sys.argv[6]
    interp = sys.argv[7]
    dim = ast.literal_eval(sys.argv[8])
    imA = piv_tls.imread(sys.argv[9])
    imB = piv_tls.imread(sys.argv[10])
    counter = int(sys.argv[11])
    print("//////////////////ADAPTIVEPIV counter =", counter, "//////////////////////"),

        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================


#
#    # configure analysis settings:

        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================

    settings = PIV.analysis.WidimSettings(init_WS=init_WS,
                                          final_WS=final_WS,
                                          WOR=WOR,
                                          n_iter_main=n_iter_main,
                                          n_iter_ref=n_iter_ref,
                                          vec_val=vec_val,
                                          interp=interp)

    print("Experimental image example")
    experimental_example(counter, imA, imB, im_number=1, settings=settings)

    #print("Synthetic image example")
    #synthetic_example(dim=dim, settings=settings)

        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================
        #==============================================FIN DE LA CONTRIBUCIÓN========================================================

