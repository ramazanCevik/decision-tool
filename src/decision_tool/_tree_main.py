import plotly.graph_objects as go
import copy
import scipy.stats as stats
import pickle
rv_type = type(stats.norm(loc=1,scale=1))

def _type_namer(e):
    """
    util
    """
    if type(e).__name__ == 'Event':
        sec = type(e.result).__name__ 
        return f"<br><br>Event, {sec}"
    else:
        sec = type(e).__name__ 
        return  f"<br><br>{sec}"
class _Parent():
    def save(self,file):
        with open(file,"wb") as f:
            pickle.dump(self,f)
def load_tree(file):
    with open(file,"rb") as f:
        return pickle.load(f)
def _type_giver(t):
    """
    util
    """
    if type(t).__name__==list.__name__:
        return ProbTree(t)
    elif type(t).__name__  ==dict.__name__:
        return DecTree(t)
    elif type(t)==tuple:
        return Event(t)
    elif (type(t)).__name__ in [(ProbTree).__name__, (DecTree).__name__,(Event).__name__]:
        return t
    elif (type(t)).__name__ == type(Tree({})).__name__:
        return _type_giver(t._structure)
    elif type(t) in [float,int]:
        return float(t)
    elif type(t).__name__ == rv_type.__name__:
        return t
    else:
        print(type(t))
        print(Tree)
        raise TypeError(f"type {type(t)} of the variable is not compatible:{t} ")

        
class ProbTree(list,_Parent):
    """
    Probability Node class. Do not use explicitly if not required, use Tree class instead.
    
    """
    def __new__(cls,*args,**kwargs):
        if not args:
            return list.__new__(cls,*args,**kwargs)
        t = args[0]
        if type(t).__name__ == ProbTree.__name__:return t
        return list.__new__(cls,*args,**kwargs)
    def __init__(self,t):
        if type(t).__name__ == ProbTree.__name__:
            self = t
            return None#list.__init__(self,t)
            
        temp = sum([i[0] for i in t])
        assert temp<1.1 and temp>0.9, f"probabilities does not add up to 1 but {temp}. {t}"
        self._solution=None
        for i in range(len(t)):
            t[i] = _type_giver(t[i]) 
        c = 1
        for i in range(len(t)):
            if t[i][-1] == None:
                t[i]  = Event((t[i][0],t[i][1],"#"+str(c)))
                c+=1   
                
        try:
            self.mean = t.mean
        except:
            self.mean = None
        
        try:
            self.var = t.var
        except:
            self.var = None
        list.__init__(self,t)

    @property
    def _type(self):
        return "ProbTree"
    # def __str__(self):
    #     return "probb"
    def __getitem__(self,items):
        if type(items).__name__ == tuple.__name__:
            if len(items)>1:
                ind = items[0]
                items = items[1:]
                return [i[1][items] for i in self if i[-1] == ind ][0] 
            else:#buraya
                items = items[0]
        return [i for i in self if i[-1] == items ][0] 
    
    def __setitem__(self, key, newvalue): 

        ind = [i.name for i in self].index(key)
        return list.__setitem__(self,ind,newvalue)
        #self[key]=newvalue
        #assert 0, "It is not possible to set to ProbTree..."
    
class DecTree(dict,_Parent):
    """
    Decision Node class. Do not use explicitly if not required, use Tree class instead.
    
    """
    def __new__(cls,*args,**kwargs):
        # print(kwargs)
        # t = kwargs.values()[0]
        # if type(t).__name__ == DecTree.__name__:return t
        return dict.__new__(cls,*args,**kwargs)
    def __init__(self,t):
        if type(t).__name__ == DecTree.__name__:
            self=t
            return None
        self._solution=None
        self.mean = None
        for i in list(t.keys()).copy():
            t[i] = _type_giver(t[i])  
        self.var = None      
        dict.__init__(self,t)
    
    def __getitem__(self,items):
        if type(items).__name__ == tuple.__name__:
            if len(items)>1:
                ind = items[0]
                items = items[1:]
                return dict.__getitem__(self,ind)[items]
            else:
                items = items[0]
        return dict.__getitem__(self,items)
    
    def __setitem__(self, key, newvalue): 
        dict.__setitem__(self,key,newvalue)
        #assert 0, "It is not possible to set to DecTree..."
    @property
    def _type(self):
        return "DecTree"
class Event(tuple):
    """
    Possible outcome of a Probtree. Do not use explicitly if not required.
    Parameters
    ----------
    t:
        tuple consisting of (probability:float,outcome:[list,dict,Tree,scipy distribution],name:hashable (optional))
    
    Examples  
    ----------
    Event((0.5,7.3,"GotHeads")) # probability=.5,outcome=7.3
    
    Event((0.5,stats.norm(loc=1,scale=2),"GotTails")) # probability=.5,outcome=normal random variable
    
    Event((0.5,stats.norm(loc=1,scale=2),"GotTails")) # probability=.5,outcome=normal random variable
    
    Event((0.5,OtherNode ,"GotTails")) # probability=.5,outcome= some other node
    
    """
    def __new__(cls,t):
        if type(t).__name__ == Event.__name__:return t
        assert t[0]>=0 and t[0]<=1 , f"probability condition does not met, given probability: {t[0]} "
        if len(t)==3:
            z = (t[0],_type_giver(t[1]),t[2])
        elif len(t)==2:
            z = (t[0],_type_giver(t[1]),None)

        return tuple.__new__(cls,z)
    @property
    def result(self):
        return self[1]
    def __init__(self,t,name=None):
        if type(t).__name__ == Event.__name__:
            self = t
            return None
            
        self.name=t[-1]
        self.prob = t[0]
        self.mean = None
        self.var = None
        self._xsqr = None
        tuple.__init__(self)
    
    def __str__(self):
        return self.__repr__()
        
    def __repr__(self):
        return "".join(["Event",str(tuple.__repr__(self))])

    @property
    def _type(self):
        return "Event"



def _mean(a):
    """
    util
    returns: mean of a.
    Parameters
    ----------
    a: any applicable element (float,int,Tree,Dectree,Probtree,Event,distribution...)
    """
    if type(a).__name__ in [int.__name__, float.__name__]:
        return a
    elif str(type(a)) in [str(DecTree), str(ProbTree),str(Event),str(Tree)]:
        return a.mean
    elif type(a).__name__ == Event.__name__:
        return _mean(a[1])
    else:
        try:
            return a.mean()
        except Exception as e:
            print(f"~~Mean of '{a}' could not be calculated ,type:{type(a)}")
            raise e

def _var(a):
    """
    util
    returns: variance of a.
    Parameters
    ----------
    a: any applicable element (float,int,Tree,Dectree,Probtree,Event,distribution...)
    """
    if type(a) in [int, float]:
        return 0
    elif str(type(a)) in [str(DecTree), str(ProbTree),str(Event),str(Tree)]:
        return a.var
    elif type(a).__name__ == Tree.__name__:
        return _var(a._structure)
    elif type(a).__name__ == Event.__name__:
        return _var(a[1])
    else:
        try:
            return a.var()
        except Exception as e:
            print(f"~~Variance of '{a}' could not be calculated ,type:{type(a)}")
            raise e
def default_objective(mean,var):
    """
    plain expectancy maximization
    returns: mean
    
    parameters
    ----------
    mean: mean of the alternative
    var: variance of the alternative
    """
    return mean




class Tree(_Parent):
    """
    Main class for decision trees.
    
    parameters
    ----------
    structure: list, dictionary, Tree, Dectree, or ProbTree resresenting a node and child nodes. 
    objective: function objective to be used at DecTree nodes.
    examples
    ---------
    problem = Tree(
        {'go':1,'do not go':stats.norm(1,2)}, 
        objective=lambda mean,var: mean-var
        )


    problem2 = Tree(
        [(.3,-1),(.4,0,),(.3,{
                                'go':2,'do not go':3})
        ]
        )
    """
    def __init__(self,structure,objective=default_objective):
        self.objective = objective
        self.xdif = 1
        self.ydif = 1
        self._structure = _type_giver(structure)
    @property
    def mean(self):
        """mean of the Tree"""
        return self._structure.mean
    @property
    def var(self):
        """variancce of the Tree"""
        return self._structure.var
    def __getitem__(self,items):
        return self._structure.__getitem__(items)
    def __str__(self):
        return self._structure.__str__()
    def __repr__(self):
        return self._structure.__repr__()
    @property
    def _type(self):
        return "Tree"
    def __color_giver(self,el):
        if type(el).__name__ == Tree.__name__:return self.__color_giver(el._structure)
        elif type(el).__name__ == DecTree.__name__:return "#ffffff"
        elif type(el).__name__ == ProbTree.__name__:return "#fffffd"
        elif type(el).__name__ in [int.__name__, float.__name__]:return  "#000000"
        elif type(el).__name__ == rv_type.__name__:return  "#dddddd"
        else: return "#000"
    def fig(self):
        """
        Returns a plotly.graph_objects.Figure instance representing the Tree.
        """
        symboldict = {"#ffffff":"square",
                      "#fffffd":"circle",
                      "#000000":"line-ew",
                      "#dddddd":"circle"} # TODO exception color
        
        color=[self.__color_giver(self)]
        node_x=[-0.0]
        node_y=[-0.0]
        node_x,node_y,edge_x,edge_y,text = [0],[0],[],[],[f"Root<br>mean:{((self.mean))}<br>var:{(_var(self))}{_type_namer(self._structure)}"]
        title = ["Root"]
        self._posgetter(self._structure,node_x,node_y,edge_x,edge_y,text,color,node_y[0],node_x[0],title)
        
        
        
        
        symbols = [symboldict[i] for i in color]
        node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hovertext=text,
            hoverinfo="text",
            text=text,
        marker=dict(
           # showscale=True,
           symbol=symbols,
            color=color,
            #text = node_x,
            size=25,

            line_width=1
            ))
        node_trace.text = text

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,hoverinfo="skip",
            line=dict(width=2, color='#000'),
            mode='lines',
                )
        if self.mean:
            solved = "Solved Tree"
        else:
            solved = "UNSOLVED Tree"
        if self.objective!=default_objective:
            try:
                solved=solved+f"   objective:{self.objective.__name__}"
            except:
                solved=solved+f"   objective:-custom-"
        title_trace = go.Scatter(
            x=node_x, y=node_y,
            text=title,
            mode='text',
                textposition="bottom center")
        fig = go.Figure(data=[edge_trace,node_trace,title_trace],
             layout=go.Layout(
                title=solved,
                titlefont_size=10,
                 #fontsize=10,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                # annotations=[ dict(
                #     showarrow=False,
                #     xref="paper", yref="paper",
                #     x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=True))
                )
        #fig.update_yaxes(showgrid=True, gridwidth=10, gridcolor='#aeebe4')
        fig.update_layout(plot_bgcolor='#ffffff')
        return fig
    @classmethod
    def _solve_structure(self,structure,objective=None):
        if type(structure).__name__ == ProbTree.__name__:

            q = ([Tree._solve_structure(i,objective=objective) for i in structure])

            structure.mean = sum([e[0]*e.mean for e in q])
            structure.var = sum([e[0]*(e._xsqr) for e in q])-structure.mean**2
            structure_ = ProbTree(q.copy())
            structure_.mean = sum([e[0]*e.mean for e in q])
            structure_.var = sum([e[0]*(e._xsqr) for e in q])-structure.mean**2
        elif type(structure).__name__ == DecTree.__name__:
            results = {i:Tree._solve_structure(structure[i],objective=objective) for i in structure.keys()}
            key = max(results.keys(),key=lambda key:objective(_mean(results[key]),_var(results[key]) )  )
            structure_ = DecTree({key:(results[key])})
            structure.mean = _mean(results[key])
            structure.var = _var(results[key])
            structure_.mean = _mean(results[key])
            structure_.var = _var(results[key])
            
        elif type(structure).__name__ == Event.__name__:

            sol = Tree._solve_structure(structure.result,objective=objective)#buraya
            structure.mean = _mean(sol)
            structure.var = _var(sol)
            structure._xsqr = structure.var+structure.mean**2
            res = sol
            if type(res).__name__ not in (int.__name__,float.__name__,rv_type.__name__):
                res = res.copy()
                res = type(sol)(res)
            structure_ = Event((tuple((structure.prob,res,structure.name))))
            structure_.mean = _mean(sol)
            structure_.var = _var(sol)
            structure_._xsqr = structure.var+structure.mean**2

        elif type(structure).__name__ == float.__name__:
            structure_ = structure
        elif type(structure).__name__ == Tree.__name__:
            Tree._solve_structure(structure._structure)
            structure_ = Tree(structure._structure.copy())
        elif type(structure).__name__ == rv_type.__name__:
            structure_=copy.deepcopy(structure)
        else:
            raise TypeError(f"type {type(structure)} of the structure is not solvable:{structure} ")

        return structure_
    
    def solve(self):
        """
        Solves the tree and saves attributes.
        Returns: optimal strategy as a Tree instance.

        Keep in mind that return strategy and parent tree references same structures. changing one will change other. 
        """
        t = Tree(Tree._solve_structure(self._structure,objective=self.objective))
        self._structure.mean = t.mean
        self._structure.var = t.var
        return t

    def _posgetter(self,t,node_x,node_y,edge_x,edge_y,text,color,py,px,title): # parents y, neighbors x
        if type(t).__name__ == DecTree.__name__:
            for key in t.keys():
                node_x.append(max(node_x)+self.xdif)
                node_y.append(py-self.ydif)
                
                tax,yax = node_x[-1],node_y[-1] 
                edge_x.append(px)
                edge_y.append(py)
                edge_x.append(px)
                edge_y.append((py+yax)/2)
                edge_x.append(tax)
                edge_y.append((py+yax)/2)
                edge_x.append(tax)
                edge_y.append(yax)
                edge_x.append(None)
                edge_y.append(None)
                
                color.append(self.__color_giver(t[key]))
                text.append(f"{key}<br>mean:{_mean(t[key])}<br>var:{_var(t[key])}{_type_namer(t[key])}")
                title.append(key)

                self._posgetter(t[key],node_x,node_y,edge_x,edge_y,text,color,node_y[-1],node_x[-1],title)
                
        elif type(t).__name__ == ProbTree.__name__:
            for e in t:
                node_x.append(max(node_x)+self.xdif)
                node_y.append(py-self.ydif)
                color.append(self.__color_giver(e[1]))
                text.append(f"{e[-1]}<br>probability:{e[0]}<br>mean:{_mean(e)}<br>var:{_var(e)}{_type_namer(e)}")  
                
                
                tax,yax = node_x[-1],node_y[-1] 
                edge_x.append(px)
                edge_y.append(py)
                edge_x.append(px)
                edge_y.append((py+yax)/2)
                edge_x.append(tax)
                edge_y.append((py+yax)/2)
                edge_x.append(tax)
                edge_y.append(yax)
                edge_x.append(None)
                edge_y.append(None)

                
                title.append(e[-1])

                self._posgetter(e   ,node_x,node_y,edge_x,edge_y,text,color,node_y[-1],node_x[-1],title)
        
        elif type(t).__name__ == Tree.__name__:
            self._posgetter(t._structure,node_x,node_y,edge_x,edge_y,text,color,node_y[-1],node_x[-1],title)
        elif type(t).__name__ == Event.__name__:
            self._posgetter(t[1],node_x,node_y,edge_x,edge_y,text,color,node_y[-1],node_x[-1],title)
            
        # elif type(t).__name__ in (int.__name__,float.__name__):
        #     pass
        # else:
        #     pass
   