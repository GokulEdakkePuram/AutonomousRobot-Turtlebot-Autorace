# Autonomous Robot — TurtleBot3 Autorace (ROS 2)

Building an autonomous racing robot from scratch: from raw LiDAR arrays in plain Python,
through simulated navigation in Gazebo, to a physical TurtleBot3 Burger driving an
autorace course under camera and LiDAR control.

Built over one semester at Ravensburg-Weingarten University (RWU) for the *Autonomous
Robots* course (SS 2025). Assessment was weighted 50/50 between a written exam and a live
demonstration of these tasks running on physical TurtleBot3 hardware — so the code here
was graded on whether it actually worked on the robot, not only in simulation.

**Final grade: 1.7** *(German scale: 1.0 is the highest mark, 4.0 the lowest pass.)*

**Stack:** ROS 2 Humble · Python · OpenCV · Gazebo · Nav2 · Docker / Docker Compose · rclpy

---

## What this repository demonstrates

| Area | Evidence |
| --- | --- |
| **ROS 2 fundamentals** | Publishers, subscribers, timers, custom nodes, `ament_python` packages, entry points, parameters |
| **ROS 2 advanced patterns** | Action servers & clients, service servers, custom `.action` / `.srv` interfaces, multi-threaded executors, callback groups, QoS profiles (`BEST_EFFORT` for sensor streams) |
| **Perception** | LiDAR scan processing and sector analysis, OpenCV lane detection (HSV masking, ROI centroids via image moments), shape-based sign detection (contour approximation) |
| **Control** | Proportional controllers for wall following and lane centering, adaptive speed based on steering error, state machines for behaviour switching |
| **Navigation** | Nav2 `NavigateToPose` action client, SLAM-produced occupancy maps, tuned `nav2_params.yaml` |
| **Reproducible environments** | Dockerfiles and Docker Compose stacks for GUI (X11), simulation, and real-robot deployment |
| **Engineering practice** | Issue-driven commits, feature branches per task, refactoring passes that removed magic numbers and duplicated logic |

---

## Repository layout

The repository is organised as a progression. Each stage builds on the previous one.

```
stage_0/  Python & LiDAR fundamentals, shell scripting, Git workflow
stage_1/  Docker & Docker Compose (build, volumes, X11 GUI forwarding)
stage_2/  ROS 2 basics — pub/sub, turtlesim control, pursuit controller
stage_3/  LiDAR-driven behaviours on TurtleBot3 in Gazebo
stage_4/  Computer vision — lane following, sign detection, obstacle avoidance
stage_5/  Capstone — the autorace course on the physical robot
```

---

### `stage_0` — Fundamentals

Plain-Python processing of recorded LiDAR scans: finding the closest valid return in a
360-point range array and converting its index into a bearing in radians using the scan's
`angle_min` / `angle_increment`. Also covers Bash scripting and the Git/SSH workflow used
throughout the project.

* [`main.py`](stage_0/main.py) — scan length, closest-point index, closest-point angle
* [`main_class.py`](stage_0/main_class.py) — the same maths refactored into a `LaserModel` class that derives the angle increment from `angle_min`/`angle_max` and replays a recorded scan stream on a loop
* [`laser-testdata_1`](stage_0/laser-testdata_1), [`laser-testdata_2`](stage_0/laser-testdata_2) — recorded scans (note the `0.0` entries: invalid returns that every later node has to filter)

Both scripts run with no arguments from any working directory, and accept a path to a
different scan file:

```bash
python3 stage_0/main.py                      # uses the bundled laser-testdata_1
python3 stage_0/main.py path/to/other-scan
python3 stage_0/main_class.py                # replays laser-testdata_2 in a loop
```

### `stage_1` — Containerisation

A hand-written [`Dockerfile`](stage_1/docker/Dockerfile) plus four Compose variants covering
the cases that actually matter when running robotics software in containers: minimal
services, custom container names, bind-mounted workspaces, and **GUI forwarding over X11**
(`DISPLAY`, `QT_X11_NO_MITSHM`, `/tmp/.X11-unix`) so Gazebo and RViz render from inside a
container.

### `stage_2` — ROS 2 basics

Four `ament_python` packages against `turtlesim`:

| Package | Node | What it does |
| --- | --- | --- |
| [`py_pubsub`](stage_2/py_pubsub/) | `talker` / `listener` | Minimal publisher/subscriber pair |
| [`turtlemover`](stage_2/turtlemover/) | `move_turtle` | Publishes `Twist` on `/turtle1/cmd_vel` to drive a circle |
| | [`circle_counter`](stage_2/turtlemover/turtlemover/count_circles.py) | Subscribes to `/turtle1/pose` and counts completed laps by tracking departure from and return to the start pose within a distance threshold |
| | [`move_turtle_topic`](stage_2/turtlemover/turtlemover/move_turtle_topic.py) | Takes a lap count on a topic, then spins two nodes cooperatively until that many circles are complete |
| [`catch_a_turtle`](stage_2/catch_a_turtle/) | `catch_a_turtle` | **Pursuit controller** — computes range and bearing to a fleeing turtle, normalises the angular error to `[-π, π]`, and applies proportional control on both linear and angular velocity with a speed cap and a capture threshold |

### `stage_3` — LiDAR behaviours in Gazebo

Moves from turtlesim to a simulated TurtleBot3 Burger, subscribing to `/scan` and
publishing to `/cmd_vel`.

* [`drive_to_wall`](stage_3/drive_to_wall/drive_to_wall/drive_to_wall.py) — drives forward and halts at a set standoff distance from the wall ahead.
* [`follow_wall`](stage_3/follow_wall/follow_wall/follow_wall_node.py) — the harder problem: detect a wall in the forward sector, rotate until the robot is *parallel* to it (by comparing two symmetric side beams), then track it. Handles `±inf` returns from the simulated LiDAR and switches controller gain depending on error magnitude. The commit history on this node (`Tweak thresholds`, `Increase linear speed`, `Adjust front dist`) is an honest record of tuning a real controller.
* [`docker-compose.yml`](stage_3/docker-compose.yml) — brings up the TurtleBot3 simulation image with `network_mode: host`, `ipc: host`, and `ROS_DOMAIN_ID` passed through, which is what lets containerised nodes talk to the robot over DDS.
* [`turtlebot_topics`](stage_3/turtlebot_topics) — the platform's topic inventory.

### `stage_4` — Computer vision

| Package | Node | Approach |
| --- | --- | --- |
| [`my_cv_package`](stage_4/my_cv_package/) | [`cv_color_detect`](stage_4/my_cv_package/my_cv_package/cv_color_detect.py) | **Lane following.** Converts frames to HSV, masks white *and* yellow lane paint, crops a bottom-centre ROI, and takes the mask's centroid via image moments. The offset from image centre becomes the steering error for a proportional controller. |
| | [`cv_view`](stage_4/my_cv_package/my_cv_package/cv_view.py) | `cv_bridge` viewer for debugging the camera stream |
| [`enter_tunnel`](stage_4/enter_tunnel/) | [`enter_tunnel`](stage_4/enter_tunnel/enter_tunnel/enter_tunnel.py) | **Sign detection.** Red HSV masking across the hue wrap-around (two ranges combined), contour filtering by area, then `approxPolyDP` to identify a *triangular* tunnel marker. On detection the robot drives in and uses the right-hand LiDAR sector to know when it has arrived. |
| [`avoid_obstacle`](stage_4/avoid_obstacle/) | [`avoid_obstacle`](stage_4/avoid_obstacle/avoid_obstacle/avoid_obstacle.py) | **Sensor fusion + state machine.** Runs LiDAR and camera on separate `MutuallyExclusiveCallbackGroup`s under a `MultiThreadedExecutor`, so perception and control never block each other. Wall-follows around obstacles with a P-controller on right-hand distance, watches the front-right sector to detect where the wall ends, and triggers a timed 90° turn when a white stop line fills enough of the ROI. |

### `stage_5` — Capstone: the real robot

The autorace course run on physical TurtleBot3 hardware. Contains the Gazebo
[`door.sdf`](stage_5/models/door.sdf) model used for the tunnel scenario.

> **Note:** the real-robot package (`autorace_real`, plus the `autorace_real_interfaces`
> package holding the custom action and service definitions) currently lives on the
> university GitLab in per-task feature branches — `38-real-bot-start-signal`,
> `39-real-bot-wall-follow`, `43-real-bot-enter-tunnel`, `44-real-follow-the-road`,
> `45-real-avoid-obstacle` — and is not yet merged here.

What that stage adds on top of stage_4, moving from simulation to hardware:

* **Action server** wrapping obstacle avoidance behind a custom `AvoidObstacle.action`, with goal, cancel, and feedback handling so the behaviour can be started, monitored, and aborted like any other ROS 2 action.
* **Service-triggered perception** — a `DetectTunnelSign.srv` service gates the vision pipeline so the camera work only runs when that leg of the course begins.
* **Nav2 integration** — once the tunnel sign is seen, the node hands off to `NavigateToPose` with a goal pose on a SLAM-generated map (`entertunnelmap`), with tuned `nav2_params.yaml`.
* **Parameterised lane following** — a single node follows either the white or the yellow line via a `follow_color` parameter, with adaptive forward speed that drops as steering error grows and LiDAR-based slow-down/stop distances.
* **Sim-to-real robustness** — real LiDAR returns `0.0` for invalid readings where Gazebo returns `inf`; the real nodes normalise this explicitly, and switch sensor subscriptions to `BEST_EFFORT` QoS to survive a lossy wireless link.
* **Deployment** — a purpose-built ROS 2 Humble Dockerfile that `colcon build`s the workspace at image build time, plus a Compose file per course leg.

---

## Running it

Everything targets **ROS 2 Humble**. The Compose files bring up the simulation image with
GUI forwarding already wired.

```bash
# start the simulation container (from stage_3 or stage_4)
export IKI_WORKSPACE=$(pwd)
export ROS_DOMAIN_ID=30
docker compose -f stage_3/docker-compose.yml up -d
docker exec -it ros2-ar-new bash
```

Inside the container, build and source the workspace, then run any node:

```bash
colcon build --symlink-install
source install/setup.bash

ros2 run drive_to_wall   drive_to_wall
ros2 run follow_wall     follow_wall_node
ros2 run my_cv_package   cv_color_detect
ros2 run avoid_obstacle  avoid_obstacle
```

The X11 forwarding in the Compose files assumes a Linux host with an X server. On macOS or
Windows, run XQuartz/VcXsrv and adjust `DISPLAY` accordingly.

---

## Notes for readers

* Commits are issue-driven (`Closes #28`), one feature branch per course task, merged into `main` — mirroring the GitLab issue board the course ran on.
* Tuning history is deliberately preserved rather than squashed. Controller gains, distance thresholds, and speeds were found empirically against the real robot, and the commit log shows that process.
* Packages carry the standard `ament_copyright` / `ament_flake8` / `ament_pep257` test scaffolding generated by `ros2 pkg create`.
* Where a node's behaviour depends on empirically-found numbers — LiDAR sector indices, HSV bounds, controller gains, standoff distances — those values come from tuning against the physical robot on the actual course, and differ from what works in Gazebo.

## License

Apache-2.0 (per-package `LICENSE` files).

## Contact

**Gokul Edakke Puram** · [GitHub](https://github.com/GokulEdakkePuram)
