from phidl import set_quickplot_options, Device, Group, quickplot as qp
import phidl.geometry as pg
import phidl.routing as pr
import numpy as np
import os

class diode_array:
    def __init__(self, params):
        self.pad_dimensions = params["pad_dimensions"]
        self.pad_pitch = params["pad_pitch"]
        self.bar_width = params["bar_width"]
        self.bar_pitch = params["bar_pitch"]
        self.num_bars = params["num_bars"]
        self.circle_radius = params["circle_radius"]
        self.bar_lengths = (self.num_bars - 1) * self.bar_pitch + self.bar_width
        self.pad_lengths = (self.num_bars - 1) * self.pad_pitch + self.pad_dimensions[0]
        self.bar_pad_spacing = params["bar_pad_spacing"]
        self.pad_route_dist = params["pad_route_dist"]
        self.route_thetas = params["route_thetas"]
        self.pad_style = params["pad_style"]
        self.interleaved_pad_spacing = params["interleaved_pad_spacing"]
        self.text_size = params["text_size"]
        self.invert_be = params["invert_be"]
        self.device = Device()
        self.be = Device()
    
    def draw_bars(self, device, be):
        vb = pg.rectangle(size = (self.bar_width, self.bar_lengths[1]), layer = 1)
        hb = pg.rectangle(size = (self.bar_lengths[0], self.bar_width), layer = 3)

        vb_array = be.add_array(vb, columns = self.num_bars[0], rows = 1, spacing = (self.bar_pitch, 0))
        vb_array.move(origin=vb_array.center, destination=(0, 0))
        hb_array = device.add_array(hb, columns = 1, rows = self.num_bars[1], spacing = (0, self.bar_pitch))
        hb_array.move(origin=hb_array.center, destination=(0, 0))

        vb_top_ports, vb_bottom_ports, hb_left_ports, hb_right_ports = [], [], [], []

        for i in range(self.num_bars[0]):
            vb_bottom_ports.append(be.add_port(midpoint = (vb_array.xmin + self.bar_width/2 + i * self.bar_pitch, vb_array.ymin), width = self.bar_width, orientation = -90, name=f"b{i}")) # bottom
            vb_top_ports.append(be.add_port(midpoint = (vb_array.xmin + self.bar_width/2 + i * self.bar_pitch, vb_array.ymax), width = self.bar_width, orientation = 90, name=f"t{i}")) # top

        for i in range(self.num_bars[1]):
            hb_left_ports.append(device.add_port(midpoint = (hb_array.xmin, hb_array.ymin + self.bar_width/2 + i * self.bar_pitch), width = self.bar_width, orientation = 180, name=f"l{i}")) # left
            hb_right_ports.append(device.add_port(midpoint = (hb_array.xmax, hb_array.ymin + self.bar_width/2 + i * self.bar_pitch), width = self.bar_width, orientation = 0, name=f"r{i}")) # right

        return [vb_array, hb_array], [vb_bottom_ports, vb_top_ports, hb_left_ports, hb_right_ports]
    
    def draw_circles(self, device):
        circle = pg.circle(radius = self.circle_radius, layer = 2)
        circle_array = device.add_array(circle, columns = self.num_bars[0], rows = self.num_bars[1], spacing = (self.bar_pitch, self.bar_pitch))
        circle_array.move(origin=circle_array.center, destination=(0, 0))
        return circle_array

    def draw_pads_single(self, device, be, pad_offset):
        v_pad_1 = pg.rectangle(size = self.pad_dimensions[:2] + 2 * self.pad_dimensions[2], layer = 1)
        v_pad_4 = pg.rectangle(size = self.pad_dimensions[:2], layer = 4)
        h_pad_3 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]) + 2 * self.pad_dimensions[2], layer = 3)
        h_pad_5 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]), layer = 5)


        v_pad_0_array_bottom = be.add_array(v_pad_1, columns = np.ceil(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_0_array_bottom.move(origin=v_pad_0_array_bottom.center, destination=(pad_offset[0], -self.bar_lengths[1]/2 - self.bar_pad_spacing[0] - self.pad_dimensions[1]/2))

        v_pad_0_array_top = be.add_array(v_pad_1, columns = np.floor(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_0_array_top.move(origin=v_pad_0_array_top.center, destination=(pad_offset[1], self.bar_lengths[1]/2 + self.bar_pad_spacing[0] + self.pad_dimensions[1]/2))

        v_pad_4_array_bottom = device.add_array(v_pad_4, columns = np.ceil(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_4_array_bottom.move(origin=v_pad_4_array_bottom.center, destination=(pad_offset[0], -self.bar_lengths[1]/2 - self.bar_pad_spacing[0] - self.pad_dimensions[1]/2))

        v_pad_4_array_top = device.add_array(v_pad_4, columns = np.floor(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_4_array_top.move(origin=v_pad_4_array_top.center, destination=(pad_offset[1], self.bar_lengths[1]/2 + self.bar_pad_spacing[0] + self.pad_dimensions[1]/2))

        h_pad_3_array_left = device.add_array(h_pad_3, columns = 1, rows = np.ceil(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_3_array_left.move(origin=h_pad_3_array_left.center, destination=(-self.bar_lengths[0]/2 - self.bar_pad_spacing[1] - self.pad_dimensions[1]/2, pad_offset[2]))

        h_pad_3_array_right = device.add_array(h_pad_3, columns = 1, rows = np.floor(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_3_array_right.move(origin=h_pad_3_array_right.center, destination=(self.bar_lengths[0]/2 + self.bar_pad_spacing[1] + self.pad_dimensions[1]/2, pad_offset[3]))

        h_pad_5_array_left = device.add_array(h_pad_5, columns = 1, rows = np.ceil(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_5_array_left.move(origin=h_pad_5_array_left.center, destination=(-self.bar_lengths[0]/2 - self.bar_pad_spacing[1] - self.pad_dimensions[1]/2, pad_offset[2]))

        h_pad_5_array_right = device.add_array(h_pad_5, columns = 1, rows = np.floor(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_5_array_right.move(origin=h_pad_5_array_right.center, destination=(self.bar_lengths[0]/2 + self.bar_pad_spacing[1] + self.pad_dimensions[1]/2, pad_offset[3]))

        top_ports, bottom_ports, left_ports, right_ports = [], [], [], []
        for i in range(self.num_bars[0]):
            if i % 2 == 0:
                bottom_ports.append(be.add_port(midpoint = (v_pad_0_array_bottom.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i/2 * self.pad_pitch,v_pad_0_array_bottom.ymax), width = self.bar_width, orientation = 90, name=f"pb{i}"))
            else:
                top_ports.append(be.add_port(midpoint = (v_pad_0_array_top.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + (i-1)/2 * self.pad_pitch,v_pad_0_array_top.ymin), width = self.bar_width, orientation = -90, name=f"pt{i}"))
        
        for i in range(self.num_bars[1]):
            if i % 2 == 0:
                left_ports.append(device.add_port(midpoint = (h_pad_3_array_left.xmax,h_pad_3_array_left.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i/2 * self.pad_pitch), width = self.bar_width, orientation = 0, name=f"pl{i}"))
            else:
                right_ports.append(device.add_port(midpoint = (h_pad_3_array_right.xmin,h_pad_3_array_right.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + (i-1)/2 * self.pad_pitch), width = self.bar_width, orientation = 180, name=f"pr{i}"))

        # text labels
        for i in range(self.num_bars[0]):
            if i % 2 == 0:
                t1 = pg.text(text=str(i), size=self.text_size, justify='left', layer=4).rotate(90)
                t1.move(origin=(t1.center[0], t1.ymax), destination=(v_pad_0_array_bottom.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i/2 * self.pad_pitch, v_pad_0_array_bottom.ymin - 20))
                device.add_ref(t1)
            else:
                t2 = pg.text(text=str(i), size=self.text_size, justify='left', layer=4).rotate(90)
                t2.move(origin=(t2.center[0], t2.ymin), destination=(v_pad_0_array_top.xmin + self.pad_dimensions[0]/2 + + self.pad_dimensions[2] + (i-1)/2 * self.pad_pitch, v_pad_0_array_top.ymax + 20))
                device.add_ref(t2)
        for i in range(self.num_bars[1]):
            if i % 2 == 0:
                t1 = pg.text(text=str(i), size=self.text_size, justify='left', layer=3)
                t1.move(origin=(t1.xmax, t1.center[1]), destination=(h_pad_3_array_left.xmin - 20, h_pad_3_array_left.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i/2 * self.pad_pitch))
                device.add_ref(t1)
            else:
                t2 = pg.text(text=str(i), size=self.text_size, justify='left', layer=3)
                t2.move(origin=(t2.xmin, t2.center[1]), destination=(h_pad_3_array_right.xmax + 20, h_pad_3_array_right.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + (i-1)/2 * self.pad_pitch))
                device.add_ref(t2)


        return [v_pad_0_array_bottom, v_pad_0_array_top, v_pad_4_array_bottom, v_pad_4_array_top, h_pad_3_array_left, h_pad_3_array_right, h_pad_5_array_left, h_pad_5_array_right], [bottom_ports, top_ports, left_ports, right_ports]
    
    def draw_pads_double(self, device, be):
        v_pad_1 = pg.rectangle(size = self.pad_dimensions[:2] + 2 * self.pad_dimensions[2], layer = 1)
        v_pad_4 = pg.rectangle(size = self.pad_dimensions[:2], layer = 4)
        h_pad_3 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]) + 2 * self.pad_dimensions[2], layer = 3)
        h_pad_5 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]), layer = 5)

        v_pad_1_array_bottom = be.add_array(v_pad_1, columns = self.num_bars[0], rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_1_array_bottom.move(origin=v_pad_1_array_bottom.center, destination=(0, -self.bar_lengths[1]/2 - self.bar_pad_spacing[0] - self.pad_dimensions[1]/2))

        v_pad_1_array_top = be.add_array(v_pad_1, columns = self.num_bars[0], rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_1_array_top.move(origin=v_pad_1_array_top.center, destination=(0, self.bar_lengths[1]/2 + self.bar_pad_spacing[0] + self.pad_dimensions[1]/2))

        v_pad_4_array_bottom = device.add_array(v_pad_4, columns = self.num_bars[0], rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_4_array_bottom.move(origin=v_pad_4_array_bottom.center, destination=(0, -self.bar_lengths[1]/2 - self.bar_pad_spacing[0] - self.pad_dimensions[1]/2))

        v_pad_4_array_top = device.add_array(v_pad_4, columns = self.num_bars[0], rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_4_array_top.move(origin=v_pad_4_array_top.center, destination=(0, self.bar_lengths[1]/2 + self.bar_pad_spacing[0] + self.pad_dimensions[1]/2))

        h_pad_3_array_left = device.add_array(h_pad_3, columns = 1, rows = self.num_bars[1], spacing = (0, self.pad_pitch))
        h_pad_3_array_left.move(origin=h_pad_3_array_left.center, destination=(-self.bar_lengths[0]/2 - self.bar_pad_spacing[1] - self.pad_dimensions[1]/2, 0))

        h_pad_3_array_right = device.add_array(h_pad_3, columns = 1, rows = self.num_bars[1], spacing = (0, self.pad_pitch))
        h_pad_3_array_right.move(origin=h_pad_3_array_right.center, destination=(self.bar_lengths[0]/2 + self.bar_pad_spacing[1] + self.pad_dimensions[1]/2, 0))

        h_pad_5_array_left = device.add_array(h_pad_5, columns = 1, rows = self.num_bars[1], spacing = (0, self.pad_pitch))
        h_pad_5_array_left.move(origin=h_pad_5_array_left.center, destination=(-self.bar_lengths[0]/2 - self.bar_pad_spacing[1] - self.pad_dimensions[1]/2, 0))

        h_pad_5_array_right = device.add_array(h_pad_5, columns = 1, rows = self.num_bars[1], spacing = (0, self.pad_pitch))
        h_pad_5_array_right.move(origin=h_pad_5_array_right.center, destination=(self.bar_lengths[0]/2 + self.bar_pad_spacing[1] + self.pad_dimensions[1]/2, 0))

        top_ports, bottom_ports, left_ports, right_ports = [], [], [], []
        for i in range(self.num_bars[0]):
                bottom_ports.append(be.add_port(midpoint = (v_pad_1_array_bottom.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch,v_pad_1_array_bottom.ymax), width = self.bar_width, orientation = 90, name=f"pb{i}"))
                top_ports.append(be.add_port(midpoint = (v_pad_1_array_top.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch,v_pad_1_array_top.ymin), width = self.bar_width, orientation = -90, name=f"pt{i}"))
        
        for i in range(self.num_bars[1]):
                left_ports.append(device.add_port(midpoint = (h_pad_3_array_left.xmax,h_pad_3_array_left.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch), width = self.bar_width, orientation = 0, name=f"pl{i}"))
                right_ports.append(device.add_port(midpoint = (h_pad_3_array_right.xmin,h_pad_3_array_right.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch), width = self.bar_width, orientation = 180, name=f"pr{i}"))

        # text labels
        for i in range(self.num_bars[0]):
            t1 = pg.text(text=str(i), size=self.text_size, justify='left', layer=4).rotate(90)
            t1.move(origin=(t1.center[0], t1.ymax), destination=(v_pad_1_array_bottom.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch, v_pad_1_array_bottom.ymin - 20))
            t2 = pg.text(text=str(i), size=self.text_size, justify='left', layer=4).rotate(90)
            t2.move(origin=(t2.center[0], t2.ymin), destination=(v_pad_1_array_top.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch, v_pad_1_array_top.ymax + 20))
            device.add_ref(t1)
            device.add_ref(t2)
        for i in range(self.num_bars[1]):
            t1 = pg.text(text=str(i), size=self.text_size, justify='left', layer=3)
            t1.move(origin=(t1.xmax, t1.center[1]), destination=(h_pad_3_array_left.xmin - 20, h_pad_3_array_left.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch))
            t2 = pg.text(text=str(i), size=self.text_size, justify='left', layer=3)
            t2.move(origin=(t2.xmin, t2.center[1]), destination=(h_pad_3_array_right.xmax + 20, h_pad_3_array_left.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch))
            device.add_ref(t1)
            device.add_ref(t2)


        return [v_pad_1_array_bottom, v_pad_1_array_top, v_pad_4_array_bottom, v_pad_4_array_top, h_pad_3_array_left, h_pad_3_array_right, h_pad_5_array_left, h_pad_5_array_right], [bottom_ports, top_ports, left_ports, right_ports]

    def draw_pads_single_line(self, device, be):
        h_pad_1 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]) + 2 * self.pad_dimensions[2], layer = 1)
        h_pad_4 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]), layer = 4)
        h_pad_3 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]) + 2 * self.pad_dimensions[2], layer = 3)
        h_pad_5 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]), layer = 5)

        h_pad_1_array_right = be.add_array(h_pad_1, columns = 1, rows = self.num_bars[0], spacing = (0, self.pad_pitch))
        h_pad_4_array_right = device.add_array(h_pad_4, columns = 1, rows = self.num_bars[0], spacing = (0, self.pad_pitch))
        h_pad_3_array_right = device.add_array(h_pad_3, columns = 1, rows = self.num_bars[1], spacing = (0, self.pad_pitch))
        h_pad_5_array_right = device.add_array(h_pad_5, columns = 1, rows = self.num_bars[1], spacing = (0, self.pad_pitch))

        larger_pads = Group([h_pad_1_array_right, h_pad_3_array_right])
        smaller_pads = Group([h_pad_4_array_right, h_pad_5_array_right])
        larger_pads.align('x')
        smaller_pads.align('x')
        larger_pads.distribute(direction='y', spacing=self.pad_pitch - self.pad_dimensions[0] - 2 * self.pad_dimensions[2])
        smaller_pads.distribute(direction='y', spacing=self.pad_pitch - self.pad_dimensions[0])

        larger_pads.move(origin=larger_pads.center, destination=(self.bar_lengths[0]/2 + self.bar_pad_spacing[1] + self.pad_dimensions[1]/2, 0))
        smaller_pads.move(origin=smaller_pads.center, destination=(self.bar_lengths[0]/2 + self.bar_pad_spacing[1] + self.pad_dimensions[1]/2, 0))

        right_ports = []

        for i in range(self.num_bars[0] + self.num_bars[1]):
                right_ports.append(device.add_port(midpoint = (h_pad_1_array_right.xmin,h_pad_1_array_right.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch), width = self.bar_width, orientation = 180, name=f"pr{i}"))

        # text labels
        for i in range(self.num_bars[0] + self.num_bars[1]):

            if i < self.num_bars[0]:
                t = pg.text(text="v" + str(i), size=self.text_size, justify='left', layer=3)
            else:
                t = pg.text(text="h" + str(i-self.num_bars[0]), size=self.text_size, justify='left', layer=3)
            t.move(origin=(t.xmin, t.center[1]), destination=(h_pad_1_array_right.xmax + 20, h_pad_1_array_right.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch))
            device.add_ref(t)


        return [h_pad_1_array_right, h_pad_4_array_right, h_pad_3_array_right, h_pad_5_array_right], right_ports

    def draw_pads_interleaved(self, device, be):
        v_pad_1 = pg.rectangle(size = self.pad_dimensions[:2] + 2 * self.pad_dimensions[2], layer = 1)
        v_pad_4 = pg.rectangle(size = self.pad_dimensions[:2], layer = 4)
        h_pad_3 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]) + 2 * self.pad_dimensions[2], layer = 3)
        h_pad_5 = pg.rectangle(size = np.flip(self.pad_dimensions[:2]), layer = 5)
    

        v_pad_1_array_bottom_1 = be.add_array(v_pad_1, columns = np.ceil(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_1_array_bottom_1.move(origin=v_pad_1_array_bottom_1.center, destination=(-self.pad_pitch/4, -self.bar_lengths[1]/2 - self.bar_pad_spacing[0] - self.pad_dimensions[1]/2))
        v_pad_1_array_bottom_2 = be.add_array(v_pad_1, columns = np.floor(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_1_array_bottom_2.move(origin=(v_pad_1_array_bottom_2.xmin, v_pad_1_array_bottom_2.ymax), destination=(v_pad_1_array_bottom_1.xmin + self.pad_pitch/2, v_pad_1_array_bottom_1.ymin - self.interleaved_pad_spacing))

        v_pad_1_array_top_1 = be.add_array(v_pad_1, columns = np.ceil(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_1_array_top_1.move(origin=v_pad_1_array_top_1.center, destination=(-self.pad_pitch/4, -v_pad_1_array_bottom_2.center[1]))
        v_pad_1_array_top_2 = be.add_array(v_pad_1, columns = np.floor(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_1_array_top_2.move(origin=v_pad_1_array_top_2.center, destination=(v_pad_1_array_bottom_2.center[0], -v_pad_1_array_bottom_1.center[1]))

        v_pad_4_array_bottom_1 = device.add_array(v_pad_4, columns = np.ceil(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_4_array_bottom_1.move(origin=v_pad_4_array_bottom_1.center, destination=(-self.pad_pitch/4, -self.bar_lengths[1]/2 - self.bar_pad_spacing[0] - self.pad_dimensions[1]/2))
        v_pad_4_array_bottom_2 = device.add_array(v_pad_4, columns = np.floor(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_4_array_bottom_2.move(origin=(v_pad_4_array_bottom_2.xmin, v_pad_4_array_bottom_2.ymax), destination=(v_pad_4_array_bottom_1.xmin + self.pad_pitch/2, v_pad_4_array_bottom_1.ymin - self.interleaved_pad_spacing - 2 * self.pad_dimensions[2]))

        v_pad_4_array_top_1 = device.add_array(v_pad_4, columns = np.ceil(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_4_array_top_1.move(origin=v_pad_4_array_top_1.center, destination=(-self.pad_pitch/4, -v_pad_4_array_bottom_2.center[1]))
        v_pad_4_array_top_2 = device.add_array(v_pad_4, columns = np.floor(self.num_bars[0]/2), rows = 1, spacing = (self.pad_pitch, 0))
        v_pad_4_array_top_2.move(origin=v_pad_4_array_top_2.center, destination=(v_pad_4_array_bottom_2.center[0], -v_pad_4_array_bottom_1.center[1]))

        h_pad_2_array_left_1 = device.add_array(h_pad_3, columns = 1, rows = np.ceil(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_2_array_left_1.move(origin=h_pad_2_array_left_1.center, destination=(-self.bar_lengths[0]/2 - self.bar_pad_spacing[1] - self.pad_dimensions[1]/2, -self.pad_pitch/4))
        h_pad_2_array_left_2 = device.add_array(h_pad_3, columns = 1, rows = np.floor(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_2_array_left_2.move(origin=(h_pad_2_array_left_2.xmax, h_pad_2_array_left_2.ymin), destination=(h_pad_2_array_left_1.xmin - self.interleaved_pad_spacing, h_pad_2_array_left_1.ymin + self.pad_pitch/2))
        
        h_pad_2_array_right_1 = device.add_array(h_pad_3, columns = 1, rows = np.ceil(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_2_array_right_1.move(origin=h_pad_2_array_right_1.center, destination=(-h_pad_2_array_left_2.center[0], h_pad_2_array_left_1.center[1]))
        h_pad_2_array_right_2 = device.add_array(h_pad_3, columns = 1, rows = np.floor(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_2_array_right_2.move(origin=h_pad_2_array_right_2.center, destination=(-h_pad_2_array_left_1.center[0], h_pad_2_array_left_2.center[1]))

        h_pad_5_array_left_1 = device.add_array(h_pad_5, columns = 1, rows = np.ceil(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_5_array_left_1.move(origin=h_pad_5_array_left_1.center, destination=(-self.bar_lengths[0]/2 - self.bar_pad_spacing[1] - self.pad_dimensions[1]/2, -self.pad_pitch/4))
        h_pad_5_array_left_2 = device.add_array(h_pad_5, columns = 1, rows = np.floor(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_5_array_left_2.move(origin=(h_pad_5_array_left_2.xmax, h_pad_5_array_left_2.ymin), destination=(h_pad_2_array_left_1.xmin - self.interleaved_pad_spacing - self.pad_dimensions[2], h_pad_5_array_left_1.ymin + self.pad_pitch/2))
        
        h_pad_5_array_right_1 = device.add_array(h_pad_5, columns = 1, rows = np.ceil(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_5_array_right_1.move(origin=h_pad_5_array_right_1.center, destination=(-h_pad_5_array_left_2.center[0], h_pad_5_array_left_1.center[1]))
        h_pad_5_array_right_2 = device.add_array(h_pad_5, columns = 1, rows = np.floor(self.num_bars[1]/2), spacing = (0, self.pad_pitch))
        h_pad_5_array_right_2.move(origin=h_pad_5_array_right_2.center, destination=(-h_pad_5_array_left_1.center[0], h_pad_5_array_left_2.center[1]))

        top_ports, bottom_ports, left_ports, right_ports = [], [], [], []
        for i in range(self.num_bars[0]):
            if i % 2 == 0:
                bottom_ports.append(be.add_port(midpoint = (v_pad_1_array_bottom_1.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i/2 * self.pad_pitch,v_pad_1_array_bottom_1.ymax), width = self.bar_width, orientation = 90, name=f"pb{i}"))
                top_ports.append(be.add_port(midpoint = (v_pad_1_array_top_1.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i/2 * self.pad_pitch,v_pad_1_array_top_1.ymin), width = self.bar_width, orientation = -90, name=f"pt{i}"))
            else:
                bottom_ports.append(be.add_port(midpoint = (v_pad_1_array_bottom_2.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + (i-1)/2 * self.pad_pitch,v_pad_1_array_bottom_2.ymax), width = self.bar_width, orientation = 90, name=f"pb{i}"))
                top_ports.append(be.add_port(midpoint = (v_pad_1_array_top_2.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + (i-1)/2 * self.pad_pitch,v_pad_1_array_top_2.ymin), width = self.bar_width, orientation = -90, name=f"pt{i}"))
        
        for i in range(self.num_bars[1]):
            if i % 2 == 0:
                left_ports.append(device.add_port(midpoint = (h_pad_2_array_left_1.xmax,h_pad_2_array_left_1.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i/2 * self.pad_pitch), width = self.bar_width, orientation = 0, name=f"pl{i}"))
                right_ports.append(device.add_port(midpoint = (h_pad_2_array_right_1.xmin,h_pad_2_array_right_1.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i/2 * self.pad_pitch), width = self.bar_width, orientation = 180, name=f"pr{i}"))
            else:
                left_ports.append(device.add_port(midpoint = (h_pad_2_array_left_2.xmax,h_pad_2_array_left_2.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + (i-1)/2 * self.pad_pitch), width = self.bar_width, orientation = 0, name=f"pl{i}"))
                right_ports.append(device.add_port(midpoint = (h_pad_2_array_right_2.xmin,h_pad_2_array_right_2.ymin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + (i-1)/2 * self.pad_pitch), width = self.bar_width, orientation = 180, name=f"pr{i}"))

        # text labels
        for i in range(self.num_bars[0]):
            t1 = pg.text(text=str(i), size=self.text_size, justify='left', layer=4).rotate(90)
            t1.move(origin=(t1.center[0], t1.ymax), destination=(v_pad_1_array_bottom_1.xmin + self.pad_dimensions[0]/2 + self.pad_dimensions[2] + i * self.pad_pitch/2, v_pad_1_array_bottom_2.ymin - 20))
            t2 = pg.text(text=str(i), size=self.text_size, justify='left', layer=4).rotate(90)
            t2.move(origin=(t2.center[0], t2.ymin), destination=(v_pad_1_array_top_1.xmin + self.pad_dimensions[0]/2 + + self.pad_dimensions[2] + i * self.pad_pitch/2, v_pad_1_array_top_1.ymax + 20))
            device.add_ref(t1)
            device.add_ref(t2)
        for i in range(self.num_bars[1]):
            t1 = pg.text(text=str(i), size=self.text_size, justify='left', layer=3)
            t1.move(origin=(t1.xmax, t1.center[1]), destination=(h_pad_2_array_left_2.xmin - 20, h_pad_2_array_left_1.ymin + self.pad_dimensions[0]/2 + i * self.pad_pitch/2))
            t2 = pg.text(text=str(i), size=self.text_size, justify='left', layer=3)
            t2.move(origin=(t2.xmin, t2.center[1]), destination=(h_pad_2_array_right_1.xmax + 20, h_pad_2_array_left_1.ymin + self.pad_dimensions[0]/2 + i * self.pad_pitch/2))
            device.add_ref(t1)
            device.add_ref(t2)

        return [v_pad_1_array_bottom_1, v_pad_1_array_bottom_2, v_pad_1_array_top_1, v_pad_1_array_top_2, v_pad_4_array_bottom_1, v_pad_4_array_bottom_2, v_pad_4_array_top_1, v_pad_4_array_top_2, h_pad_2_array_left_1, h_pad_2_array_left_2, h_pad_2_array_right_1, h_pad_2_array_right_2, h_pad_5_array_left_1, h_pad_5_array_left_2, h_pad_5_array_right_1, h_pad_5_array_right_2], [bottom_ports, top_ports, left_ports, right_ports]
 
    def route_pads_double(self, device, be, bar_ports, pad_ports, thetas):
        for i in range(self.num_bars[0]):
            dx = abs(bar_ports[0][i].midpoint[0] - pad_ports[0][i].midpoint[0])
            dy = abs(bar_ports[0][i].midpoint[1] - pad_ports[0][i].midpoint[1])
            offset = dy - self.pad_route_dist - dx / np.tan(thetas[0])
            be.add_ref(pr.route_sharp(pad_ports[0][i], bar_ports[0][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=1))
            be.add_ref(pr.route_sharp(pad_ports[1][i], bar_ports[1][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=1))
        
        for i in range(self.num_bars[1]):
            dx = abs(bar_ports[2][i].midpoint[0] - pad_ports[2][i].midpoint[0])
            dy = abs(bar_ports[2][i].midpoint[1] - pad_ports[2][i].midpoint[1])
            offset = dx - self.pad_route_dist - dy / np.tan(thetas[1])
            device.add_ref(pr.route_sharp(pad_ports[2][i], bar_ports[2][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=3))
            device.add_ref(pr.route_sharp(pad_ports[3][i], bar_ports[3][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=3))

    def route_pads_single(self, device, be, bar_ports, pad_ports, thetas):
        h_extender = pg.rectangle(size = (self.bar_width, self.bar_width), layer = 3)
        h_extender_array_1 = device.add_array(h_extender, columns = 1, rows = np.ceil(self.num_bars[1]//2), spacing = (0, self.bar_pitch * 2))
        h_extender_array_2 = device.add_array(h_extender, columns = 1, rows = np.floor(self.num_bars[1]//2), spacing = (0, self.bar_pitch * 2))
        h_extender_array_1.move(origin=(h_extender_array_1.xmin, h_extender_array_1.ymin + self.bar_width/2), destination=bar_ports[3][0].midpoint)
        h_extender_array_2.move(origin=(h_extender_array_2.xmax, h_extender_array_2.ymin + self.bar_width/2), destination=bar_ports[2][1].midpoint)

        v_extender = pg.rectangle(size = (self.bar_width, self.bar_width), layer = 1)
        v_extender_array_1 = be.add_array(v_extender, rows=1, columns=np.ceil(self.num_bars[0]//2), spacing=(self.bar_pitch * 2, 0))
        v_extender_array_2 = be.add_array(v_extender, rows=1, columns=np.floor(self.num_bars[0]//2), spacing=(self.bar_pitch * 2, 0))
        v_extender_array_1.move(origin=(v_extender_array_1.xmin + self.bar_width/2, v_extender_array_1.ymin), destination=bar_ports[1][0].midpoint)
        v_extender_array_2.move(origin=(v_extender_array_2.xmin + self.bar_width/2, v_extender_array_2.ymax), destination=bar_ports[0][1].midpoint)
        
        for i in range(self.num_bars[0]):
            if i % 2 == 0:
                dx = abs(bar_ports[0][i].midpoint[0] - pad_ports[0][i//2].midpoint[0])
                dy = abs(bar_ports[0][i].midpoint[1] - pad_ports[0][i//2].midpoint[1])
                offset = dy - self.pad_route_dist - dx / np.tan(thetas[0])
                if dx == 0:
                    be.add_ref(pr.route_sharp(pad_ports[0][i//2], bar_ports[0][i], path_type="manhattan", layer=1))
                else:
                    be.add_ref(pr.route_sharp(pad_ports[0][i//2], bar_ports[0][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=1))
            else:
                dx = abs(bar_ports[1][i].midpoint[0] - pad_ports[1][(i-1)//2].midpoint[0])
                dy = abs(bar_ports[1][i].midpoint[1] - pad_ports[1][(i-1)//2].midpoint[1])
                offset = dy - self.pad_route_dist - dx / np.tan(thetas[0])
                if dx == 0:
                    be.add_ref(pr.route_sharp(pad_ports[1][(i-1)//2], bar_ports[1][i], path_type="manhattan", layer=1))
                else:
                    be.add_ref(pr.route_sharp(pad_ports[1][(i-1)//2], bar_ports[1][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=1))
        
        for i in range(self.num_bars[1]):
            if i % 2 == 0:
                dx = abs(bar_ports[2][i].midpoint[0] - pad_ports[2][i//2].midpoint[0])
                dy = abs(bar_ports[2][i].midpoint[1] - pad_ports[2][i//2].midpoint[1])
                offset = dx - self.pad_route_dist - dy / np.tan(thetas[1])
                if dy == 0:
                    device.add_ref(pr.route_sharp(pad_ports[2][i//2], bar_ports[2][i], path_type="manhattan", layer=3))
                else:
                    device.add_ref(pr.route_sharp(pad_ports[2][i//2], bar_ports[2][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=3))
            else:
                dx = abs(bar_ports[3][i].midpoint[0] - pad_ports[3][(i-1)//2].midpoint[0])
                dy = abs(bar_ports[3][i].midpoint[1] - pad_ports[3][(i-1)//2].midpoint[1])
                offset = dx - self.pad_route_dist - dy / np.tan(thetas[1])
                if dy == 0:
                    device.add_ref(pr.route_sharp(pad_ports[3][(i-1)//2], bar_ports[3][i], path_type="manhattan", layer=3))
                else:
                    device.add_ref(pr.route_sharp(pad_ports[3][(i-1)//2], bar_ports[3][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=3))

    def route_pads_interleaved(self, device, be, bar_ports, pad_ports, thetas):
        for i in range(self.num_bars[0]):
            if i % 2 == 0:
                dx = abs(bar_ports[0][i].midpoint[0] - pad_ports[0][i].midpoint[0])
                dy = abs(bar_ports[0][i].midpoint[1] - pad_ports[0][i].midpoint[1])
                offset = dy - self.pad_route_dist - dx / np.tan(thetas[0])
                be.add_ref(pr.route_sharp(pad_ports[0][i], bar_ports[0][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=1))
                be.add_ref(pr.route_sharp(pad_ports[1][i], bar_ports[1][i], path_type="Z", length1=self.pad_route_dist + self.interleaved_pad_spacing + self.pad_dimensions[1] + 2 * self.pad_dimensions[2], length2=offset, layer=1))

            else:
                dx = abs(bar_ports[1][i].midpoint[0] - pad_ports[1][i].midpoint[0])
                dy = abs(bar_ports[1][i].midpoint[1] - pad_ports[1][i].midpoint[1])
                offset = dy - self.pad_route_dist - dx / np.tan(thetas[0])
                be.add_ref(pr.route_sharp(pad_ports[1][i], bar_ports[1][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=1))
                be.add_ref(pr.route_sharp(pad_ports[0][i], bar_ports[0][i], path_type="Z", length1=self.pad_route_dist + self.interleaved_pad_spacing + self.pad_dimensions[1] + 2 * self.pad_dimensions[2], length2=offset, layer=1))

        
        for i in range(self.num_bars[1]):
            if i % 2 == 0:
                dx = abs(bar_ports[2][i].midpoint[0] - pad_ports[2][i].midpoint[0])
                dy = abs(bar_ports[2][i].midpoint[1] - pad_ports[2][i].midpoint[1])
                offset = dx - self.pad_route_dist - dy / np.tan(thetas[1])
                device.add_ref(pr.route_sharp(pad_ports[2][i], bar_ports[2][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=3))
                device.add_ref(pr.route_sharp(pad_ports[3][i], bar_ports[3][i], path_type="Z", length1=self.pad_route_dist + self.interleaved_pad_spacing + self.pad_dimensions[1] + 2 * self.pad_dimensions[2], length2=offset, layer=3))

            else:
                dx = abs(bar_ports[3][i].midpoint[0] - pad_ports[3][i].midpoint[0])
                dy = abs(bar_ports[3][i].midpoint[1] - pad_ports[3][i].midpoint[1])
                offset = dx - self.pad_route_dist - dy / np.tan(thetas[1])
                device.add_ref(pr.route_sharp(pad_ports[3][i], bar_ports[3][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=3))
                device.add_ref(pr.route_sharp(pad_ports[2][i], bar_ports[2][i], path_type="Z", length1=self.pad_route_dist + self.interleaved_pad_spacing + self.pad_dimensions[1] + 2 * self.pad_dimensions[2], length2=offset, layer=3))

    def route_pads_single_line(self, device, be, bar_ports, pad_ports, thetas):
        h_extender = pg.rectangle(size = (self.bar_width, self.bar_width), layer = 3)
        h_extender_array = device.add_array(h_extender, columns = 1, rows = self.num_bars[1], spacing = (0, self.bar_pitch))
        h_extender_array.move(origin=(h_extender_array.xmax, h_extender_array.ymin + self.bar_width/2), destination=bar_ports[2][0].midpoint)

        v_extender = pg.rectangle(size = (self.bar_width, self.bar_width), layer = 1)
        v_extender_array = be.add_array(v_extender, rows=1, columns=self.num_bars[0], spacing=(self.bar_pitch, 0))
        v_extender_array.move(origin=(v_extender_array.xmin + self.bar_width/2, v_extender_array.ymin), destination=bar_ports[1][0].midpoint)


        for i in range(self.num_bars[0]):
            be.add_ref(pr.route_sharp(pad_ports[i], bar_ports[0][i], path_type="manhattan", layer=1)) 

        for i in range(self.num_bars[1]):
            dx = abs(bar_ports[3][i].midpoint[0] - pad_ports[i+self.num_bars[0]].midpoint[0])
            dy = abs(bar_ports[3][i].midpoint[1] - pad_ports[i+self.num_bars[0]].midpoint[1])
            offset = dx - self.pad_route_dist - dy / np.tan(thetas[1])
            if dy == 0:
                device.add_ref(pr.route_sharp(pad_ports[i+self.num_bars[0]], bar_ports[3][i], path_type="manhattan", layer=3))
            else:
                device.add_ref(pr.route_sharp(pad_ports[i+self.num_bars[0]], bar_ports[3][i], path_type="Z", length1=self.pad_route_dist, length2=offset, layer=3))
    
    def draw(self, show_ports = False, show_subports = False, single_pad_offsets = [0, 0, 0, 0]):
        set_quickplot_options(show_ports = show_ports, show_subports = show_subports)
        bars, bar_ports = self.draw_bars(self.device, self.be)
        circles = self.draw_circles(self.device)
        if self.pad_style == "double":
            pads, pad_ports = self.draw_pads_double(self.device, self.be)
            self.route_pads_double(self.device, self.be, bar_ports, pad_ports, self.route_thetas)

        elif self.pad_style == "single":
            pads, pad_ports = self.draw_pads_single(self.device, self.be, single_pad_offsets)
            self.route_pads_single(self.device, self.be, bar_ports, pad_ports, self.route_thetas)
        elif self.pad_style == "interleaved":
            pads, pad_ports = self.draw_pads_interleaved(self.device, self.be)
            self.route_pads_interleaved(self.device, self.be, bar_ports, pad_ports, self.route_thetas)

        elif self.pad_style == "single_line":
            pads, pad_ports = self.draw_pads_single_line(self.device, self.be)
            self.route_pads_single_line(self.device, self.be, bar_ports, pad_ports, self.route_thetas)
            be_ref = self.device.add_ref(self.be)
        else:
            raise ValueError("Invalid pad style")
        
        if self.pad_style != "single_line":
            if self.invert_be:
                bbox = pg.rectangle(size = (self.device.xsize + 20, self.be.ysize + 20), layer = 0)
                bbox.move(origin=bbox.center, destination=(0, 0))
                inverted = pg.boolean(bbox, self.be, operation = 'A-B', layer=1)
                self.device.add_ref(inverted)
            else:
                self.device.add_ref(self.be)
        else:
            if self.invert_be:
                bbox = pg.rectangle(size = (self.device.xsize + 20, self.device.ysize + 20), layer = 0)
                bbox.move(origin=bbox.center, destination=self.device.center)
                inverted = pg.boolean(bbox, self.be, operation = 'A-B', layer=1)
                self.device.add_ref(inverted)
                self.device.remove(be_ref)
        
        qp(self.device)

    def save(self, directory, filename):
        self.device.write_gds(os.path.join(directory, filename + ".gds"), cellname=filename)