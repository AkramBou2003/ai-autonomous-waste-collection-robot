# System operation

The final version of the project is intended to work as follows: the camera sends images to YOLOv3, the vehicle moves according to the position of the detected bottle, and the arm uses preset servo angles after the vehicle stops.

```mermaid
flowchart TD
    A[Camera image] --> B[YOLOv3 bottle detection]
    B --> C{Bottle found?}
    C -- No --> D[Turn slowly to search]
    D --> A
    C -- Yes --> E[Find bottle position]
    E --> F{Bottle near image centre?}
    F -- No --> G[Turn left or right]
    G --> A
    F -- Yes --> H{Bottle box large enough?}
    H -- No --> I[Move forward]
    I --> A
    H -- Yes --> J[Stop vehicle]
    J --> K[Run preset arm movement]
```

The box size is only an estimate of how close the bottle is; this version does not include obstacle detection or mapping. Test the complete sequence on the actual robot and calibrate it before operation.
