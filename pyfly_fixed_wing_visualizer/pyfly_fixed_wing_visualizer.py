# AUTOGENERATED! DO NOT EDIT! File to edit: pyfly_fixed_wing_visualizer.ipynb (unless otherwise specified).

__all__ = ['simrecorder']

# Cell
class simrecorder:


    class prog():
        '''
        Progressbar class. Used for displaying the progress during simulation and rendering. Requires tqdm.
        '''
        def __init__(self,max_it, name, unit, pos):
            from tqdm.notebook import tqdm
            self.bar = tqdm(total=max_it, position=pos, leave=True, unit=unit, desc=name)

        def update(self,val):
            self.bar.update(val)

        def disable(self):
            self.bar.disable=True

    def __init__(self, simduration):
        '''
        Initialize main class, used for recording, plotting
        '''
        import numpy as np
        self.simduration = simduration # In sim.dt steps
        self.simpb = self.prog(simduration,'Simulating',' Step',0) # progressbar for simulation

        ## Arrays used for storing simulation results
        self.res_n = np.zeros(simduration)
        self.res_e = np.zeros(simduration)
        self.res_d = np.zeros(simduration)
        self.roll = np.zeros(simduration)
        self.pitch = np.zeros(simduration)
        self.yaw = np.zeros(simduration)


    def savestate(self, state, idd):
        '''
        This function is called every step of the simulation
        and passed simulation object as well as the current simulation step
        '''
        self.res_n[idd] = state['position_n'].value
        self.res_e[idd] = state['position_e'].value
        self.res_d[idd] = state['position_d'].value
        self.roll[idd] = state['roll'].value
        self.pitch[idd] = state['pitch'].value
        self.yaw[idd] = state['yaw'].value

        self.simpb.update(1) # Update progressbar

    def read_obj(self, filename):
        '''
        from https://gist.github.com/yzhong52/7c3e0b3a201af45f0cd12f10e06b9d95
        load a .obj file into triangles and vertices
        '''
        import numpy as np

        triangles = []
        vertices = []
        with open(filename) as file:
            for line in file:
                components = line.strip(' \n').split(' ')
                if components[0] == "f": # face data
                    # e.g. "f 1/1/1/ 2/2/2 3/3/3 4/4/4 ..."
                    indices = list(map(lambda c: int(c.split('/')[0]) - 1, components[1:]))
                    for i in range(0, len(indices) - 2):
                        triangles.append(indices[i: i+3])
                elif components[0] == "v": # vertex data
                    # e.g. "v  30.2180 89.5757 -76.8089"
                    vertex = list(map(lambda c: float(c), components[1:]))
                    vertices.append(vertex)
        return np.array(vertices), np.array(triangles)



    def rotation_matrix(self, axis, theta):
        import math
        import numpy as np
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.
        """
        axis = np.asarray(axis)
        axis = axis / math.sqrt(np.dot(axis, axis))
        a = math.cos(theta / 2.0)
        b, c, d = -axis * math.sin(theta / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                         [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                         [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])



    def plot(self, rotate=180, interval = 10):
        '''
        Main plotting functions accepting the following optional parameters:
            - rotate: azimuth rotation of final 3D plot.
            - interval:
        '''
        from IPython.core.display import HTML
        import matplotlib.pyplot as plt
        import mpl_toolkits.mplot3d.axes3d as p3
        import matplotlib.animation as animation
        import numpy as np

        self.fig = plt.figure(figsize=(10,10))
        self.fig.suptitle('')

        data = [self.res_n, self.res_e, self.res_d]

        #
        # top left plot
        ax1 = self.fig.add_subplot(2, 2, 1)
        ax1.set_xlim([np.min(self.res_n)-2,np.max(self.res_n)+2])
        ax1.set_xlabel('X')
        ax1.set_ylim([np.min(self.res_e)-2,np.max(self.res_e)+2])
        ax1.set_ylabel('Y')

        # top right plot
        ax2 = self.fig.add_subplot(2, 2, 2)
        ax2.set_xlim([np.min(self.res_n)-2,np.max(self.res_n)+2])
        ax2.set_xlabel('X')
        ax2.set_ylim([np.min(self.res_d)-2,np.max(self.res_d)+2])
        ax2.set_ylabel('Z')

        # bottom left plot
        self.ax = self.fig.add_subplot(2, 2, 3, projection='3d') #TODO: self needed here (see update_lines)?
        self.ax.set_xlim3d([np.min(data)-2,np.max(data)+2])
        self.ax.set_xlabel('X')
        self.ax.set_ylim3d([np.min(data)-2,np.max(data)+2])
        self.ax.set_ylabel('Y')
        self.ax.set_zlim3d([np.min(data)-2,np.max(data)+2])
        self.ax.set_zlabel('Z')

        # bottom right plot
        ax3 = self.fig.add_subplot(2, 2, 4)
        ax3.set_xlim([np.min(self.res_e)-2,np.max(self.res_e)+2])
        ax3.set_xlabel('Y')
        ax3.set_ylim([np.min(self.res_d)-2,np.max(self.res_d)+2])
        ax3.set_ylabel('Z')

        self.ax.set_title('')  #TODO: self needed here (see update_lines)?
        ax1.set_title('') # XY plottitle
        ax2.set_title('') # XZ plottitle
        ax3.set_title('') # YZ plottitle

        #l oad drone 3D model
        vertices, self.triangles = self.read_obj("Wing.obj")

        # scaling drone 3D model (this is currently at an arbitrary scale)
        self.drone_x = vertices[:,0]*0.15
        self.drone_y = vertices[:,1]*0.15
        self.drone_z = vertices[:,2]*0.15

        #Rotate Drone into correct initial orientation
        done = np.dot(self.rotation_matrix([0,0,1], np.pi/2), [self.drone_x,self.drone_y,self.drone_z])
        done = np.dot(self.rotation_matrix([1,0,0], np.pi/2), done)
        [self.drone_x,self.drone_y,self.drone_z] = np.dot(self.rotation_matrix([0,1,0], np.pi), done)

        self.drone=[self.drone_x,self.drone_y,self.drone_z]




        lines=[0,0,0,0]

        lines[0], = self.ax.plot(data[0][0:1], data[1][0:1], data[2][0:1])
        lines[1], = ax1.plot([], [], lw=2)
        lines[2], = ax2.plot([], [], lw=2)
        lines[3], = ax3.plot([], [], lw=2)


        # Creating the Animation object
        self.pb = self.prog(500, 'Drawing', ' Frame',0)
        anim = animation.FuncAnimation(self.fig, self.update_lines, 500, fargs=(data, lines, rotate),
                                           interval=interval, blit=False)

        return HTML(anim.to_html5_video())



    # Calculates Rotation Matrix given euler angles.
    def eulerAnglesToRotationMatrix(self, theta) :
        import math
        import numpy as np
        R_x = np.array([[1,         0,                  0                   ],
                        [0,         math.cos(theta[0]), -math.sin(theta[0]) ],
                        [0,         math.sin(theta[0]), math.cos(theta[0])  ]
                        ])



        R_y = np.array([[math.cos(theta[1]),    0,      math.sin(theta[1])  ],
                        [0,                     1,      0                   ],
                        [-math.sin(theta[1]),   0,      math.cos(theta[1])  ]
                        ])

        R_z = np.array([[math.cos(theta[2]),    -math.sin(theta[2]),    0],
                        [math.sin(theta[2]),    math.cos(theta[2]),     0],
                        [0,                     0,                      1]
                        ])


        R = np.dot(R_z, np.dot( R_y, R_x ))

        return R


    def update_lines(self, num, dataLines, lines, rotate):
        import numpy as np
        self.pb.update(1)

        cnt = 0

        for line in lines:
            # NOTE: there is no .set_data() for 3 dim data...
            if str(type(line)) == '''<class 'matplotlib.lines.Line2D'>''':
                if cnt == 0:
                    line.set_data(dataLines[0][:num],dataLines[1][:num])
                elif cnt ==1:
                    line.set_data(dataLines[0][:num],dataLines[2][:num])
                else:
                    line.set_data(dataLines[1][:num],dataLines[2][:num])
                cnt = cnt + 1
            else:
                if len(self.ax.collections):
                    self.ax.collections.pop()

                line.set_data(dataLines[0][:num],dataLines[1][:num])

                line.set_3d_properties(dataLines[2][:num])

                ### Here is probably most optimization potential!!##########
                ### Are the signs correct???
                ### are thes euler angles or not???

                #yaw_rot = self.rotation_matrix([0,0,1], self.yaw[num])
                #roll_rot = self.rotation_matrix([0,1,0], self.roll[num])
                #pitch_rot = self.rotation_matrix([1,0,0], self.pitch[num])

                #drone = np.dot(yaw_rot, self.drone)
                #drone = np.dot(np.dot(roll_rot,yaw_rot), drone)
                #drone = np.dot(np.dot(pitch_rot,np.dot(roll_rot,yaw_rot)), drone)

                drone = np.dot(self.eulerAnglesToRotationMatrix([self.roll[num],self.yaw[num],self.pitch[num]]), self.drone)

                ##############################################################
                # ax.plot_trisurf(x, z, triangles, y, shade=True, color='white')
                self.ax.plot_trisurf(drone[0]+dataLines[0][num], drone[2]+dataLines[1][num], self.triangles, drone[1]+dataLines[2][num], shade=True, color='red')
                self.ax.view_init(elev=15., azim=45+rotate*num/self.simduration) # 15, 45

        return lines
