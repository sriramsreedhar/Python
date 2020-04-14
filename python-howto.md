```python
#Q1 - Reversing list using slice operator
a=[1,2,3,3,4]
print(a[::-1])

```

    [4, 3, 3, 2, 1]



```python
#Q2 - adding list using sum function
a=[2,4,6,5]
sum(a)

```




    17




```python
#Q3 - Adding list using iteration
a=[2,4,6,5,3,2,2]

list_sum=0
for i in a:
    list_sum += i
    
print(list_sum)

```

    24


#Q4 - Doubling the number in the list using iterator
a=[4,2,2,2,5,22,100]

#i=0
for i in a:
    b=i+i
    print(b)
    


```python
#Q5 - Get the numbers from the list
list_1=['aaa',1,2,'bbb',22]

#b=[i for i in lista if isinstance(lista, (int))]
#list_2 = [i for i in list_1 if isinstance(i, (int, float))]
2

list_2 = [i for i in list_1 if isinstance(i, (int, float))]
print(list_2)
addme=0


for i in list_2:
    addme+=i
    
print(addme)
    
    

```

    [1, 2, 22]
    25



```python

```


```python

```
