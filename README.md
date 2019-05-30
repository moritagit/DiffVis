# DiffVis


Visualizes difference between two sequences.

<span style="color: green;">す</span><span style="color: green;">も</span><span style="color: green;">も</span><span style="color: green;">も</span><span style="color: red;">桃</span><span style="color: green;">も</span><span style="color: red;">桃</span><span style="color: green;">\u3000</span><span style="color: green;">\u3000</span><span style="color: green;">の</span><span style="color: green;">う</span><span style="color: green;">ち</span><span style="color: green;"> 1</span><span style="color: green;"> 2</span><span style="color: red;"> 3</span><span style="color: green;"> 4</span><br><span style="color: green;">す</span><span style="color: green;">も</span><span style="color: green;">も</span><span style="color: green;">も</span><span style="color: blue;">も</span><span style="color: green;">も</span><span style="color: blue;">も</span><span style="color: blue;">も</span><span style="color: blue;">も</span><span style="color: green;">の</span><span style="color: green;">う</span><span style="color: green;">ち</span><span style="color: green;"> 1</span><span style="color: green;"> 2</span><span style="color: blue;"> 4</span><span style="color: green;"> 4</span>



## Requirements

* Python3



## Usage

This module can be used in your cord like:

```python
from DiffVis.diffvis import DiffVis
from IPython.display import HTML

source = 'すももも桃も桃のうち1234'
target = 'すもももももももものうち1244'

dv = DiffVis(source, target)
dv.build()

# output to console
print(dv.visualize(mode='console', padding=True))

# output HTML
HTML(dv.visualize(mode='html', padding=True))
```


## Install

To install, simply clone from GitHub.

```console
git clone https://github.com/moritagit/DiffVis.git
```



## References

* [visedit](https://pypi.org/project/visedit/)
