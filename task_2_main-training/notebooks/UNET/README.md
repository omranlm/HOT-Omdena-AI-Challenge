The pretrained weights can be accessed [here](https://drive.google.com/drive/folders/1xJRJ_QIvNE6Lq0TAzfOQBS8iDGjASyT_?usp=sharing)

You can load the model using the following commands 

```
#define paths to load the model from
path_to_load_json = ''
path_to_load_model = ''

# load json and create model
json_file = open(path_to_load_json, 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)

# load weights into new model
loaded_model.load_weights(path_to_load_model)
print("Loaded model from disk")
```

