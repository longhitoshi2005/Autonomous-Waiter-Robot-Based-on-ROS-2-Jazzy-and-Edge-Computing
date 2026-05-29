# Autonomous Robot Waiter System

## Project Proposal

## 1. Project Title

**Development of an Autonomous Robot Waiter System Using ROS2, Computer
Vision, and Embedded Control**

------------------------------------------------------------------------

## 2. Introduction

The global hospitality industry is increasingly facing significant
challenges due to labor shortages, rising operational costs, and the
need for improved service efficiency. Restaurants and service
environments often rely heavily on human waiters to perform repetitive
tasks such as delivering food, transporting items, and guiding
customers.

To address these challenges, robotic service systems are emerging as a
promising solution. Autonomous service robots can assist human staff by
performing repetitive delivery tasks, improving service efficiency while
reducing workload.

This project proposes the development of an **Autonomous Robot Waiter
System**, designed to navigate indoor restaurant environments, detect
obstacles, and deliver items to designated locations.

The system integrates multiple disciplines including: - Robotics -
Artificial Intelligence - Embedded Systems - Mechanical Engineering -
Human--Robot Interaction

------------------------------------------------------------------------

## 3. Problem Statement

Restaurants and service facilities frequently encounter the following
operational challenges: - High labor demand for routine service tasks -
Inefficient manual delivery processes - Increased operational costs -
Difficulty maintaining consistent service quality

An autonomous robotic assistant that can handle repetitive delivery
tasks would significantly improve operational efficiency and allow staff
to focus on customer interaction.

------------------------------------------------------------------------

## 4. Project Objectives

The main objective is to design and implement an **autonomous robotic
waiter capable of navigating indoor environments and delivering items to
specific locations**.

Specific objectives: 1. Develop a mobile robotic platform capable of
indoor navigation. 2. Implement autonomous navigation using **LIDAR and
ROS2**. 3. Integrate **computer vision for obstacle detection**. 4.
Develop communication between **edge computer and microcontroller**. 5.
Create a **touchscreen GUI interface** for robot control. 6. Build a
fully integrated robot prototype.

------------------------------------------------------------------------

## 5. Proposed System Overview

The proposed system consists of two layers.

### High-Level Processing System

Handled by **Intel UP 4000 Edge Computer**.

Responsibilities: - Running ROS2 - Processing LIDAR data - Running
computer vision models - Navigation and decision making

### Low-Level Control System

Handled by **ESP32-S3 (YOLO UNO board)**.

Responsibilities: - Motor control - Servo control - Hardware interface -
Communication with edge computer

Communication protocol: **I2C**

------------------------------------------------------------------------

## 6. Hardware Components

### ESP32S3-N16R8 (YOLO UNO)

Functions: - Motor control - Sensor interface - Hardware-level control

Firmware: **MicroPython (YOLO UNO v1.12)**

### Intel UP 4000

Functions: - AI processing - ROS2 execution - Navigation algorithms

### USB Camera

Used for: - Object detection - Obstacle detection - ArUco marker
recognition

### LIDAR

Used for: - Environment mapping - Distance measurement - Autonomous
navigation

### USB Speaker

Used for voice notifications and human‑robot interaction.

### LCD Touchscreen

Used as robot control interface.

### Battery

Provides portable power for all robot components.

------------------------------------------------------------------------

## 7. Mechanical Components

### Robot Frame

Constructed using: - 3D printed frame - Plastic structural frame

### Omni Wheels (4)

Advantages: - Smooth movement - High maneuverability

### Servo Motors (2)

Used for mechanisms such as tray lifting.

### Encoder Motors (2)

Provide locomotion and speed feedback.

### Fasteners

Bolts, screws, and nuts used for structural assembly.

------------------------------------------------------------------------

## 8. Software Architecture

### Motor Control Module

Runs on ESP32 with MicroPython.

### Navigation System

Runs on ROS2 using: - LIDAR - SLAM - Path planning

### Computer Vision Module

Model: **YOLOv5n**

Functions: - Obstacle detection - Object detection

### Marker Detection

Uses **ArUco markers** for location identification.

### GUI Interface

Allows user to: - Select destination - Start/stop robot - Monitor system
status

### Communication Protocol

UP 4000 → Master\
YOLO UNO → Slave

Protocol: **I2C**

------------------------------------------------------------------------

## 9. System Architecture Diagram

        LCD Touchscreen
              |
              v
    +---------------------+
    |   Intel UP 4000     |
    | ROS2 + AI + SLAM    |
    +---------+-----------+
              |
       I2C Communication
              |
              v
    +---------------------+
    |     ESP32-S3        |
    |     YOLO UNO        |
    |  Motor Controller   |
    +----+-----------+----+
         |           |
         v           v
     Motors        Servos
         |
         v
     Robot Chassis
    (Omni Wheels + Frame)

    Sensors connected to UP4000:
    - LIDAR
    - USB Camera

------------------------------------------------------------------------

## 10. Expected Outcomes

### Robot Prototype

A functional robot capable of: - Autonomous navigation - Obstacle
detection - Destination-based movement

### Software System

Includes: - Motor control firmware - ROS2 navigation system - Computer
vision models - GUI control interface - I2C communication

### Documentation

Includes: - Hardware design - Software architecture - Testing results

### Demonstration

The robot demonstrates autonomous navigation and delivery capability.
