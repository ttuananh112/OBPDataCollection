# OBPDataCollection
### Data collection for module Object Behavior Prediction in carla simulation

### 1. Data structure:

* Rasterization: a color-encoded image of all map? <br>
  Data-type: image


* Vectorization: topology <br>
  Data-type: table(csv) <br>
--> Be divided into 2 type: static and dynamic <br> 

  * Static: such as lane, crosswalk, ... <br>
    * id .......( group by <br>
    * type .....to get object ) <br>
    * x ........( point's position .... | absolute <br>
    * y ........... of shape... ) ........ | value <br>
    
  * Dynamic: such as vehicle, pedestrian, traffic light, ... <br>
  has property and state <br>
    * Property:
      * id
      * type
      * width
      * length
    * State:
      * timestamp
      * id
      * center_x ... ( center point ... | ... absolute ... | also be
      * center_y ........ of object ... ) | ... value .........| ground-truth
      * heading .... (yaw - align with map orientation)
      * status: depend on object type
        * red/yellow/green for traffic light
        * velocity for moving object
        * ... <br>
      
      |--> Data will be saved as short scene (~20 seconds?)

### 2. Folder structure:
```
- Prediction
    |__ Scene1
    |   |__ Images
    |       |__ 10000000.jpeg
    |       |__ 10000001.jpeg
    |           ...
    |   |__ static.csv
    |   |__ Dynamic
    |       |__ property.csv
    |       |__ state.csv
    |
    |__ Scene2
        ...
```

### 3. Addition:
- Current object type:

| Static         | Dynamic       |
| -------------- | ------------- |
| waypoint       | car           |
| l_lane         | motorbike     |
| r_lane         | traffic_light |
| crosswalk      | pedestrian    |
| [traffic_sign] | bicycle       |

* [traffic_sign] could be any type of traffic sign, for example:
  * speed_limit.30
  * speed_limit.60
  * speed_limit.90
  * ...
* pedestrian and bicycle have not been supported yet.

### 4. TODO:

- A lot of things to do...
