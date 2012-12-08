#!/usr/bin/env python
#scene.py - Construct/display SVG scenes.
#with influence from http://code.activestate.com/recipes/325823-draw-svg-images-in-python/

import os,sys

def colorstr(rgb): return "#%x%x%x" % (rgb[0]/16,rgb[1]/16,rgb[2]/16)

class Scene:
    def __init__(self,name="svg",width=8.5,height=11,units="in",stroke_width=.005):
        self.name = name
        self.layers = []
        self.height = height
        self.width = width
        self.units = units
        self.stroke_width = stroke_width
        return

    #copy constructor
    @classmethod
    def from_scene(cls,other_scene,name): 
        assert(name != other_scene.name)
        return cls(name,other_scene.width,other_scene.height,other_scene.units,other_scene.stroke_width)

    def add_layer(self,layer): 
        self.layers.append(layer)
    def add_layers(self,layers):
        for layer in layers:
            self.layers.append(layer)
    def add_group(self,group):
        for item,layer in group.items.iteritems():
            layer.add(item)
    def remove_duplicates(self):
        for layer in self.layers:
            new_items = [layer.items[-1]]
            for i,item in enumerate(layer.items[:-1]):
                found = 0
                for other in layer.items[i+1:]:
                    if item.key() == other.key():
                        found = 1
                if not found:
                    new_items.append(item)
            layer.items = new_items


    def strarray(self):
        var = ["<?xml version=\"1.0\" ?>\n",
               "<svg xmlns=\"http://www.w3.org/2000/svg\"\n",
               "  height=\"%f%s\" width=\"%f%s\" \n" % (self.height,self.units,self.width,self.units),
               "  units=\"%s\"\n"%(self.units),
               "  viewBox=\"0 0 %f %f\">\n"%(self.width,self.height),
               " <g fill=\"none\" stroke-width=\"%f\"\n"%(self.stroke_width),
               "    transform=\"translate(%f,%f) scale(1, -1)\">\n"%\
               (.5*self.width,.5*self.height)]
        for layer in self.layers: 
            var += layer.strarray()
        var += [" </g>\n</svg>\n"]
        return var

    def write_svg(self,filename=None):
        if filename:
            self.svgname = filename
        else:
            self.svgname = self.name + ".svg"
        file = open(self.svgname,'w')
        file.writelines(self.strarray())
        file.close()
        return

    def display(self,prog='display'):
        os.system("%s %s &" % (prog,self.svgname))
        return

    def convert(self,format='.ps'):
        if format=='.ps':
            os.system('inkscape %s.svg -P %s.ps' % (self.name,self.name) )
        if format=='.dxf':
            os.system('inkscape %s.svg -P %s.tmp.ps' % (self.name,self.name) )
            os.system('pstoedit %s.tmp.ps -f dxf:-ctl %s.dxf' % (self.name,self.name) )
            os.system('rm %s.tmp.ps' % (self.name))
        return 


#layers will hold groups of shapes with same attributes
class Layer:
    def __init__(self,name,color,scene):
        self.color = color
        self.items = []
        self.name = name
        self.scene = scene
        scene.add_layer(self)
    def __repr__(self):
        return self.name

    def add(self,item): 
        try: self.items.extend(item)
        except(TypeError):
            self.items.append(item)

    def strarray(self):
        var = ["<g stroke=\"%s\">\n" % colorstr(self.color)]
        for item in self.items: var += item.strarray(self.scene)
        var += [" </g>\n"]
        return var

    def mirror(self,p,v):
        for i,item in enumerate(self.items):
            self.items[i] = item.mirror(p,v)
    def rotate(self,p,t):
        for i,item in enumerate(self.items):
            self.items[i] = item.rotate(p,t)
    def translate(self,t):
        for i,item in enumerate(self.items):
            self.items[i] = item.translate(t)


#this will allow instancing, transforms, etc. on a group while preserving layers
#of input geometry through a dictionary
class Group:
    def __init__(self,items=None):
        self.items={}
        if items:
            for item,layer in items.iteritems():
                self.items[item] = layer

    def add(self,items):
        for item,layer in items.iteritems():
            self.items[item] = layer

    def add_group(self,group):
        for item,layer in group.items.iteritems():
            self.items[item] = layer


    def mirror(self,p,v,copy=False):
        new = {}
        if copy:
            new.update(self.items)
        for item,layer in self.items.iteritems():
            new[item.mirror(p,v)] = layer
        return Group(new)

    def rotate(self,p,t,copy=False):
        new = {}
        if copy:
            new.update(self.items)
        for item,layer in self.items.iteritems():
                new[item.rotate(p,t)] = layer
        return Group(new)

    def rotates(self,p,ts):
        new = {}
        for t in ts:
            for item,layer in self.items.iteritems():
                    new[item.rotate(p,t)] = layer
        return Group(new)

    def translate(self,ts,copy=False):
        new = {}
        if copy:
            new.update(self.items)
        for t in ts:
            for item,layer in self.items.iteritems():
                new[item.translate(t)] = layer
        return Group(new)