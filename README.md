### BooleanTRN

This project deals with automatic TRN generation from given experimental data.

### Network Format

This library used special data format for saving the networks data. In this
each file line represents single network. Each line is separated by Unix
newline character `\n`.

```text
network1
network2
network3
...
```

Each line consists of `list` of `tuples` representing network data. First
character is always left square bracket `[` while last character is always
right square bracket `]`. Each tuple is separated by comma `,`

```text
[ tuple1, tuple2, .... ]
```

Each tuple represents district **interaction** (or edge) of the network. This
tuple consists fo sequence of integers or `None`. Each position represents
specific characteristic feature of that interaction. Following are specifics of
each position inside the tuple

1. Source Node/Vertex (any integer)
2. Destination Node/Vertex (any integer or `None`)
3. Type of interaction (0, 1 or `None`)
4. Type of logic gate on destination node (0, 1 or `None`)
5. Other attributes (if needed)

First 4 positions are mandatory. Each tuple should have **at least** 4
positions representing above features. All nodes will be converted into
integers. Most likely you will have specific network with labels. In that case
please convert your all nodes into appropriate integers which will act as
an `ID` for given node and will be represented in this network format.

Only Node/Vertex can be added as `(ID, None, None, None)` where `ID`
represents the ID of the node in given network.

Example network file

```python
[(0, 0, 1, None), (0, 1, 1, None)]
[(0, 2, 1, 0), (1, 0, 1, 0)]
[(2, 0, 1, None), (1, 3, 1, None)]
```

File will be read through python's default `csv` package. Hence, use double
quote if you are using any `string` in the attributes. In addition, `None`
can be converted into `null` while saving the file (as done by `csv` module).

