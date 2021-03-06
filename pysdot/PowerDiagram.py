from .domain_types import ConvexPolyhedraAssembly
from .radial_funcs import RadialFuncUnit
from .cpp import cpp_module
import numpy as np
import os


class PowerDiagram:
    def __init__(self, positions=None, weights=None, domain=None, radial_func=RadialFuncUnit()):
        self.radial_func = radial_func

        self.positions = None
        self.weights = None
        self.domain = None

        self._positions_are_new = True
        self._weights_are_new = True
        self._domain_is_new = True
        self._inst = None

        if not ( domain is None ):
            self.set_domain( domain )
        if not ( positions is None ):
            self.set_positions( positions )
        if not ( weights is None ):
            self.set_weights( weights )

    def set_positions(self, positions):
        self._positions_are_new = True
        self.positions = positions

    def set_weights(self, weights):
        self._weights_are_new = True
        self.weights = weights

    def set_domain(self, domain):
        self._domain_is_new = True
        self.domain = domain

    def integrals(self):
        inst = self._updated_grid()
        return inst.integrals(
            self.positions,
            self.weights,
            self.domain._inst,
            self.radial_func.name()
        )

    def centroids(self):
        inst = self._updated_grid()
        return inst.centroids(
            self.positions,
            self.weights,
            self.domain._inst,
            self.radial_func.name()
        )

    def der_integrals_wrt_weights(self, stop_if_void=False):
        inst = self._updated_grid()
        return inst.der_integrals_wrt_weights(
            self.positions,
            self.weights,
            self.domain._inst,
            self.radial_func.name(),
            stop_if_void
        )

    def der_centroids_and_integrals_wrt_weight_and_positions(self):
        inst = self._updated_grid()
        return inst.der_centroids_and_integrals_wrt_weight_and_positions(
            self.positions,
            self.weights,
            self.domain._inst,
            self.radial_func.name()
        )

    def display_vtk(self, filename, points=False, centroids=False):
        dn = os.path.dirname(filename)
        if len(dn):
            os.makedirs(dn, exist_ok=True)
        inst = self._updated_grid()
        return inst.display_vtk(
            self.positions,
            self.weights,
            self.domain._inst,
            self.radial_func.name(),
            filename,
            points,
            centroids
        )

    def display_vtk_points(self, filename, points=None):
        if points is None:
            return self.display_vtk_points(filename, self.positions)
        dn = os.path.dirname(filename)
        if len(dn):
            os.makedirs(dn, exist_ok=True)
        inst = self._updated_grid()
        return inst.display_vtk_points(
            self.positions,
            filename
        )

    # make a .asy file for a representation of the power diagram
    def display_asy(self, filename, preamble="", closing="", output_format="pdf", linewidth=0.02, dotwidth=0.0, values=np.array([]), colormap="inferno", avoid_bounds=False, min_rf=1, max_rf=0):
        dn = os.path.dirname( filename )
        if len( dn ):
            os.makedirs( dn, exist_ok = True )

        p = "settings.outformat = \"{}\";\nunitsize(1cm);\n".format( output_format )
        if linewidth > 0:
            p += "defaultpen({}cm);\n".format( linewidth )
        elif dotwidth > 0:
            p += "defaultpen({}cm);\n".format( dotwidth / 6 )
        p += preamble

        inst = self._updated_grid()
        inst.display_asy(
            self.positions,
            self.weights,
            self.domain._inst,
            self.radial_func.name(),
            filename,
            p,
            values,
            colormap,
            linewidth,
            dotwidth,
            avoid_bounds,
            closing,
            min_rf,
            max_rf
        )

    #
    def display_jupyter(self, disp_centroids=True, disp_positions=True, disp_ids=True):
        inst = self._updated_grid()
        path = inst.display_html_canvas(
            self.positions,
            self.weights,
            self.domain._inst,
            self.radial_func.name()
        )

        jsct = """
            (function() {
            // geometry
            var path = new Path2D();
            __paths__

            // display parameters
            var disp_centroids = __disp_centroids__, disp_positions = __disp_positions__, disp_ids = __disp_ids__;
            var cr = 0.52 * Math.max( max_x - min_x, max_y - min_y );
            var cx = 0.5 * ( max_x + min_x );
            var cy = 0.5 * ( max_y + min_y );
            var orig_click_x = 0;
            var orig_click_y = 0;
            var pos_click_x = 0;
            var pos_click_y = 0;

            // canvas
            var canvas = document.createElement( "canvas" );
            canvas.style.overflow = "hidden";
            // canvas.style.width = 940;
            canvas.height = 400;
            canvas.width = 940;

            element.append( canvas );

            function draw() {
                var w = canvas.width, h = canvas.height;
                var m = 0.5 * Math.min( w, h );
                var s = m / cr;

                var ctx = canvas.getContext( '2d' );

                ctx.setTransform( 1, 0, 0, 1, 0, 0 );
                ctx.clearRect( 0, 0, w, h );

                ctx.lineWidth = 1;
                ctx.font = '16px serif';
                ctx.strokeStyle = "#FF0000";
                for( var i = 0; i < centroids.length; ++i ) {
                    var px = ( centroids[ i ][ 0 ] - cx ) * s + 0.5 * w;
                    var py = ( centroids[ i ][ 1 ] - cy ) * s + 0.5 * h;
                    if ( disp_ids ) {
                        ctx.fillText( String( i ), px + 5, py );
                    }

                    if ( disp_centroids ) {
                        ctx.beginPath();
                        ctx.arc( px, py, 2, 0, 2 * Math.PI, true );
                        ctx.stroke();
                    }
                }

                ctx.translate( 0.5 * w, 0.5 * h );
                ctx.scale( s, s );
                ctx.translate( - cx, - cy );

                var c = 1.0 / s;
                ctx.lineWidth = c;
                ctx.strokeStyle = "#000000";
                ctx.stroke( path );

                ctx.strokeStyle = "#0000FF";
                if ( disp_positions ) {
                    for( var i = 0; i < diracs.length; ++i ) {
                        ctx.beginPath();
                        ctx.moveTo( diracs[ i ][ 0 ] - 4 * c, diracs[ i ][ 1 ] );
                        ctx.lineTo( diracs[ i ][ 0 ] + 4 * c, diracs[ i ][ 1 ] );
                        ctx.stroke();

                        ctx.beginPath();
                        ctx.moveTo( diracs[ i ][ 0 ], diracs[ i ][ 1 ] - 4 * c );
                        ctx.lineTo( diracs[ i ][ 0 ], diracs[ i ][ 1 ] + 4 * c );
                        ctx.stroke();
                    }
                }
            }

            canvas.addEventListener( "wheel", function( e ) {  
                if ( e.shiftKey ) {
                    var w = canvas.width, h = canvas.height;
                    var r = canvas.getBoundingClientRect();
                    var m = 0.5 * Math.min( w, h );
                    var s = m / cr;

                    var d = Math.pow( 2, ( - e.wheelDeltaY / 200.0 || e.deltaY / 5.0 ) );
                    cx -= ( e.x - r.x - 0.5 * w ) * ( d - 1 ) / s;
                    cy -= ( e.y - r.y - 0.5 * h ) * ( d - 1 ) / s;
                    cr *= d;

                    draw();
                    return false;
                }
            }, false );

            canvas.addEventListener( "mousedown", function( e ) {  
                orig_click_x = e.x;
                orig_click_y = e.y;
                pos_click_x = e.x;
                pos_click_y = e.y;
            } );

            canvas.addEventListener( "mousemove", function( e ) {  
                if ( e.buttons == 1 || e.buttons == 4 ) {
                    var w = canvas.width, h = canvas.height;
                    var m = 0.5 * Math.min( w, h );
                    var s = m / cr;

                    cx -= ( e.x - pos_click_x ) / s;
                    cy -= ( e.y - pos_click_y ) / s;
                    pos_click_x = e.x;
                    pos_click_y = e.y;

                    draw();
                }
            } );

            draw();
            })();
        """

        jsct = jsct.replace( "\n            ", "\n" )
        jsct = jsct.replace( "__disp_centroids__", str( 1 * disp_centroids ) )
        jsct = jsct.replace( "__disp_positions__", str( 1 * disp_positions ) )
        jsct = jsct.replace( "__disp_ids__", str( 1 * disp_ids ) )
        jsct = jsct.replace( "__paths__", path )

        import IPython
        return IPython.display.Javascript( jsct )

    def _updated_grid(self):
        # default values
        if self.positions is None:
            raise RuntimeError( "positions in PowerDiagram must be specified" )

        if self.domain is None:
            domain = ConvexPolyhedraAssembly()
            domain.add_box([0, 0], [1, 1])
            self.set_domain( domain )

        if self.weights is None:
            self.set_weights( np.ones( self.positions.shape[ 0 ] ) )

        # check types
        if not isinstance(self.positions, np.ndarray):
            self.positions = np.array(self.positions)
        if not isinstance(self.weights, np.ndarray):
            self.weights = np.array(self.weights)

        # instantiation of PowerDiagram
        if not self._inst:
            assert(self.positions.dtype == self.domain._type)
            assert(self.weights.dtype == self.domain._type)
            module = cpp_module.module_for_type_and_dim(
                self.domain._type, self.positions.shape[1]
            )
            self._inst = module.PowerDiagramZGrid(11)

        self._inst.update(
            self.positions,
            self.weights,
            self._positions_are_new or self._domain_is_new,
            self._weights_are_new or self._domain_is_new,
            self.radial_func.name()
        )
        self._positions_are_new = False
        self._weights_are_new = False
        self._domain_is_new = False

        return self._inst
