# DiffVis


Visualizes difference between two sequences.

![result](https://github.com/moritagit/DiffVis/blob/doc/figures/result_html_table.png "result")



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

If you tokenize the strings, output will be like:

![result tokenized](https://github.com/moritagit/DiffVis/blob/doc/figures/result_tokenized_html_table.png "result tokenized")



## Install

To install, simply clone from GitHub.

```console
git clone https://github.com/moritagit/DiffVis.git
```



## References

* [visedit](https://pypi.org/project/visedit/)
