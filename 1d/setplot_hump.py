#!/usr/bin/env python
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 

import numpy as np

# Plot customization
import matplotlib

# Markers and line widths
matplotlib.rcParams['lines.linewidth'] = 2.0
matplotlib.rcParams['lines.markersize'] = 6
matplotlib.rcParams['lines.markersize'] = 8

# Font Sizes
matplotlib.rcParams['font.size'] = 16
matplotlib.rcParams['axes.labelsize'] = 15
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['xtick.labelsize'] = 12
matplotlib.rcParams['ytick.labelsize'] = 12

# DPI of output images
# matplotlib.rcParams['savefig.dpi'] = 300 # Publication quality
matplotlib.rcParams['savefig.dpi'] = 100

# Need to do this after the above
import matplotlib.pyplot as mpl

from clawpack.pyclaw.solution import Solution

from multilayer.aux import bathy_index,kappa_index,wind_index
import multilayer.plot as plot

# matplotlib.rcParams['figure.figsize'] = [6.0,10.0]



#--------------------------
def setplot(plotdata,wave_family,rho,dry_tolerance):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of pyclaw.plotters.data.ClawPlotData.
    Output: a modified version of plotdata.
    
    """
    
    # Load bathymetry
    b = Solution(0,path=plotdata.outdir,read_aux=True).state.aux[bathy_index,:]

    def bathy(cd):
        return b
    
    def kappa(cd):
        return Solution(cd.frameno,path=plotdata.outdir,read_aux=True).state.aux[kappa_index,:]

    def wind(cd):
        return Solution(cd.frameno,path=plotdata.outdir,read_aux=True).state.aux[wind_index,:]
    
    def h_1(cd):
        return cd.q[0,:] / rho[0]
    
    def h_2(cd):
        return cd.q[2,:] / rho[1]
        
    def eta_2(cd):
        return h_2(cd) + bathy(cd)
        
    def eta_1(cd):
        return h_1(cd) + eta_2(cd)
        
    def u_1(cd):
        index = np.nonzero(h_1(cd) > dry_tolerance)
        u_1 = np.zeros(h_1(cd).shape)
        u_1[index] = cd.q[1,index] / cd.q[0,index]
        return u_1
        
    def u_2(cd):
        index = np.nonzero(h_2(cd) > dry_tolerance)
        u_2 = np.zeros(h_2(cd).shape)
        u_2[index] = cd.q[3,index] / cd.q[2,index]
        return u_2
    
    
    def jump_afteraxes(current_data):
        # Plot position of jump on plot
        mpl.hold(True)
        mpl.plot([0.5,0.5],[-10.0,10.0],'k--')
        mpl.plot([0.0,1.0],[0.0,0.0],'k--')
        mpl.hold(False)
        mpl.title('')

    plotdata.clearfigures()  # clear any old figures,axes,items data
    
    #------------------------
    # Window Settings
    #------------------------

    # Full frame limits
    xlimits = [-2000.,4000.0]
    ylimits_depth = [-3300.,100.]

    # Semi-zoom limits
    xlimits_depth_zoomed = [-2000.,3500.]
    ylimits_depth_zoomed = [-120.,100.]

    # Zoom on internal surface
    xlimits_depth_zoomed_internal = [-100.,3500.]
    ylimits_depth_zoomed_internal = [-100.5,-97.5]

    # Zoom on top surface
    xlimits_depth_zoomed_surface = [-100.,3500.]
    ylimits_depth_zoomed_surface = [-2., 5.]

    # Momentum and velocity limits
    ylimits_momentum = [-0.004,0.004]
    ylimits_velocities = [-0.8,0.8]
    
    # ========================================================================
    #  Depth and Momentum Plot
    # ========================================================================
    plotfigure = plotdata.new_plotfigure(name='Depth and Velocity',figno=14)
    plotfigure.show = True
    
    def twin_axes(cd):
        fig = mpl.gcf()
        fig.clf()
        
        # Get x coordinate values
        x = cd.patch.dimensions[0].centers
        
        # Create axes for each plot, sharing x axis
        depth_axes = fig.add_subplot(211)
        vel_axes = fig.add_subplot(212) #,sharex=depth_axes)     # the velocity scale
        
        # Bottom layer
        depth_axes.fill_between(x,bathy(cd),eta_2(cd),color=plot.bottom_color)
        # Top Layer
        depth_axes.fill_between(x,eta_2(cd),eta_1(cd),color=plot.top_color)
        # Plot bathy
        depth_axes.plot(x,bathy(cd),'k',linestyle=plot.bathy_linestyle)
        # Plot internal layer
        depth_axes.plot(x,eta_2(cd),'k')#,linestyle=plot.internal_linestyle)
        # Plot surface
        depth_axes.plot(x,eta_1(cd),'k')#,linestyle=plot.surface_linestyle)
        
        # Remove ticks from top plot
        num_ticks = len(depth_axes.xaxis.get_ticklocs())
        depth_axes.xaxis.set_ticklabels(["" for n in xrange(num_ticks)])
        
        # ax1.set_title('')
        depth_axes.set_title('t = %3.2f' % (cd.t))
        depth_axes.set_xlim(xlimits)
        depth_axes.set_ylim(ylimits_depth)
        # depth_axes.set_xlabel('x')
        depth_axes.set_ylabel('Depth (m)')
        
        # Bottom layer velocity
        bottom_layer = vel_axes.plot(x,u_2(cd),'k',linestyle=plot.internal_linestyle,label="Bottom Layer Velocity")
        # Top Layer velocity
        top_layer = vel_axes.plot(x,u_1(cd),'b',linestyle=plot.surface_linestyle,label="Top Layer velocity")

        # Add legend
        vel_axes.legend(loc=4)
        vel_axes.set_title('')
        # vel_axes.set_title('Layer Velocities')
        vel_axes.set_ylabel('Velocities (m/s)')
        vel_axes.set_xlabel('x (m)')
        vel_axes.set_xlim(xlimits)
        vel_axes.set_ylim(ylimits_velocities)
        
        # Add axis labels (not sure why this needs to be done)
        locs = vel_axes.xaxis.get_ticklocs()
        vel_axes.xaxis.set_ticklabels([str(loc) for loc in locs])
        
        # This does not work on all versions of matplotlib
        try:
            mpl.subplots_adjust(hspace=0.1)
        except:
            pass
    
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.afteraxes = twin_axes

    # ========================================================================
    #  Depth and Momentum Plot semi-zoom (not showing bathymetry, but still 
    #   showing both layers of water)
    # ========================================================================
    plotfigure = plotdata.new_plotfigure(name='Depth and Velocity - semi-zoom',figno=15)
    plotfigure.show = True
    
    def twin_axes(cd):
        fig = mpl.gcf()
        fig.clf()
        
        # Get x coordinate values
        x = cd.patch.dimensions[0].centers
        
        # Create axes for each plot, sharing x axis
        depth_axes = fig.add_subplot(211)
        vel_axes = fig.add_subplot(212) #,sharex=depth_axes)     # the velocity scale
        
        # Bottom layer
        depth_axes.fill_between(x,bathy(cd),eta_2(cd),color=plot.bottom_color)
        # Top Layer
        depth_axes.fill_between(x,eta_2(cd),eta_1(cd),color=plot.top_color)
        # Plot bathy
        depth_axes.plot(x,bathy(cd),'k',linestyle=plot.bathy_linestyle)
        # Plot internal layer
        depth_axes.plot(x,eta_2(cd),'k')#,linestyle=plot.internal_linestyle)
        # Plot surface
        depth_axes.plot(x,eta_1(cd),'k')#,linestyle=plot.surface_linestyle)
        
        # Remove ticks from top plot
        num_ticks = len(depth_axes.xaxis.get_ticklocs())
        depth_axes.xaxis.set_ticklabels(["" for n in xrange(num_ticks)])
        
        # ax1.set_title('')
        depth_axes.set_title('t = %3.2f' % (cd.t))
        depth_axes.set_xlim(xlimits_depth_zoomed)
        depth_axes.set_ylim(ylimits_depth_zoomed)
        # depth_axes.set_xlabel('x')
        depth_axes.set_ylabel('Depth (m)')
        
        # Bottom layer velocity
        bottom_layer = vel_axes.plot(x,u_2(cd),'k',linestyle=plot.internal_linestyle,label="Bottom Layer Velocity")
        # Top Layer velocity
        top_layer = vel_axes.plot(x,u_1(cd),'b',linestyle=plot.surface_linestyle,label="Top Layer velocity")

        # Add legend
        vel_axes.legend(loc=4)
        vel_axes.set_title('')
        # vel_axes.set_title('Layer Velocities')
        vel_axes.set_ylabel('Velocities (m/s)')
        vel_axes.set_xlabel('x (m)')
        vel_axes.set_xlim(xlimits)
        vel_axes.set_ylim(ylimits_velocities)
        
        # Add axis labels (not sure why this needs to be done)
        locs = vel_axes.xaxis.get_ticklocs()
        vel_axes.xaxis.set_ticklabels([str(loc) for loc in locs])
        
        # This does not work on all versions of matplotlib
        try:
            mpl.subplots_adjust(hspace=0.1)
        except:
            pass
    
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.afteraxes = twin_axes
    
    # ========================================================================
    #  Depth plot zoom
    # ========================================================================
    plotfigure = plotdata.new_plotfigure(name='Depth Zoomed',figno=16)
    plotfigure.show = True

    def twin_axes_zoomed(cd):
        fig = mpl.gcf()
        fig.clf()
        
        # Get x coordinate values
        x = cd.patch.dimensions[0].centers
        
        # Create axes for each plot, sharing x axis
        surface_axes = fig.add_subplot(211)
        internal_axes = fig.add_subplot(212) 
        
        # Bottom layer
        internal_axes.fill_between(x,bathy(cd),eta_2(cd),color=plot.bottom_color)
        internal_axes.fill_between(x,eta_2(cd),eta_1(cd),color=plot.top_color)

        # Top Layer
        surface_axes.fill_between(x,bathy(cd),eta_2(cd),color=plot.bottom_color)
        surface_axes.fill_between(x,eta_2(cd),eta_1(cd),color=plot.top_color)

        # Plot bathy
        internal_axes.plot(x,bathy(cd),color='k',linestyle=plot.bathy_linestyle)

        # Plot internal layer
        internal_axes.plot(x,eta_1(cd),'k')
        internal_axes.plot(x,eta_2(cd),'k')

        # Plot surface
        surface_axes.plot(x,eta_1(cd),'k')
        surface_axes.plot(x,eta_2(cd),'k')

        # Plot markers for begining and end of slope
        surface_axes.plot([0,0],[-32000, 100],'--k')
        internal_axes.plot([0,0],[-32000, 100],'--k')
        internal_axes.plot([2500, 2500],[-32000, 100],'--k')
        surface_axes.plot([2500, 2500],[-32000, 100],'--k')

        # Remove ticks from top plot
        num_ticks = len(surface_axes.xaxis.get_ticklocs())
        surface_axes.xaxis.set_ticklabels(["" for n in xrange(num_ticks)])
        
        surface_axes.set_title('t = %3.2f' % (cd.t))
        surface_axes.set_xlim(xlimits_depth_zoomed_surface)
        surface_axes.set_ylim(ylimits_depth_zoomed_surface)
        surface_axes.set_ylabel('Depth (m)')

        internal_axes.set_title('')
        internal_axes.set_xlim(xlimits_depth_zoomed_internal)
        internal_axes.set_ylim(ylimits_depth_zoomed_internal)
        internal_axes.set_xlabel('x (m)')
        internal_axes.set_ylabel('Depth (m)')
        
        # Add axis labels (not sure why this needs to be done)
        locs = internal_axes.xaxis.get_ticklocs()
        internal_axes.xaxis.set_ticklabels([str(loc) for loc in locs])
        
        # This does not work on all versions of matplotlib
        try:
            mpl.subplots_adjust(hspace=0.1)
        except:
            pass
    
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.afteraxes = twin_axes_zoomed
    
    # ========================================================================
    #  Momentum
    # ========================================================================
    plotfigure = plotdata.new_plotfigure(name="momentum",figno=134)
    plotfigure.show = False
    
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = "Momentum"
    plotaxes.xlimits = xlimits
    plotaxes.ylimits = ylimits_momentum
    
    # Top layer
    plotitem = plotaxes.new_plotitem(plot_type='1d')
    plotitem.plot_var = 1
    plotitem.plotstyle = 'b-'
    plotitem.show = True
    
    # Bottom layer 
    plotitem = plotaxes.new_plotitem(plot_type='1d')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'k-'
    plotitem.show = True

    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    # plotdata.print_framenos = [0,20,25,30,50]      # list of frames to print
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?

    return plotdata

    
