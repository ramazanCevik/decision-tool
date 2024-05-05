# Project description
Decision-tool is a simple yet effective decision analysis tool. Solves and visualizes Trees with recursive algorithm.

## Usage
Decision trees are constructed using `Tree` class. it takes nested structure and returns a Tree instance. In the nested structure, dictinary represents decision, List represents discrete probability distribution and tuple represents possible outcome of a discrete probability distribution, scipy.stats can be used for continous probability distribution:


```
example_tree = Tree({"option 1":25,
                     "option 2":[(.4,20,"result 1"), (.3,21,"result 2"), (.3,stats.norm(1,1),"result 3")]
                     })
example_tree.fig().show()
```
![Image](https://i.imgur.com/TmRLdVp.png)




Consider the example: You have 2 options as quit the job and not quit. if you quit, you will get a bonus of 8000. If you do not quit, you will promote to manager with a probability of 0.3, If you then quit, will get 16000, If you do not, you will get a random payoff distributed normally with mean 12000 and standart deviation of 1000. If you do not quit at the begining and do not promote, your PV will be normal random variable with mean 10000 and standart deviation of 3000.

```
job_decision = Tree({
    "quit":8e3,
    "do not quit":[(0.3, 
                        {"quit":16e3,
                        "do not quit":stats.norm(12e3,1e3)
                        }
                    ,"promote"),

                    (0.7, stats.norm(10e3,3e3),"do not promote")
                    ]
})

job_decision.fig().show()
```
![Image](https://i.imgur.com/jxHMaBZ.png)

The method `solve` returns a Tree instance that only contains optimal solutions.
```
solution = job_decision.solve()
print("optimal expected monetary value:" ,solution.mean,"variance:",solution.var)
solution.fig().show()

    
```
    optimal expected monetary value: 11800.0 variance: 13860000.0
![Image](https://i.imgur.com/dEx2H6v.png)

For indexing, order decision names and event names:
```
print("Variance of not quiting and not getting a promote ",
      solution["do not quit","do not promote"].var)

```
    Variance of not quiting and not getting a promote  9000000.0

Save and load decision trees using `save` method and `load_tree` function.