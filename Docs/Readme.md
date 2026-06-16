# Mind2Sketch Servers

A distributed services architecture(with some deviation from true microservices for simplicity) backend system for generating and manipulating AI-generated face images using style vectors of StyleGAN2 and advanced image mixing techniques. The system processes image generation/manipulation requests, applies style transformations, and manages image data through a distributed task queue.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [System Requirements](#system-requirements)
- [Services](#services)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [Running the Services](#running-the-services)
- [Scaling Inference](#scaling-for-higher-inference-throughput)

## Project Overview

Mind2Sketch Servers is a system that is intended to ochestrate the server side processes of project Mind2Sketch.:

- **Image Generation**: Create images from various inputs like random seeds, existing images etc.
- **Style Mixing**: Blend multiple image styles.
- **Image Editing**: Apply edits and style adjustments to existing images
- **Data Retrieval**: Query and manage generated images and metadata

The system uses:

- **Message Queue**: Redis + Celery for distributed task processing
- **Database**: MongoDB for storing image metadata and generation history
- **Cloud Storage**: Minio (or AWS S3) for image persistence
- **APIs**: FastAPI for HTTP endpoints

## Architecture

### [High Level Architecture](https://excalidraw.com/#json=zsODTS53qD7l3fwz2WU9o,mM291kREB87jpOWm-gbvyg)



![High Level Architecture](./high-level-architecture.png)



### Component Interaction Flow

```
Client Request
      ↓
Handler (FastAPI)
→ Validates Request
→ Minor Preprocessing (if needed)
→ Determines Required Pipeline
      ↓
(Optional) Preprocessing Queue
→ Preprocessor Worker
→ Style Mixing / Preprocessing
      ↓
Generation Queue
→ Generator Worker
→ Image Generation
      ↓
Result Storage (MongoDB + Minio/S3)
      ↓
Retriever (FastAPI)
→ Returns Images & Metadata to Client
```

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **GPU**: NVIDIA GPU with CUDA support (recommended for generation/preprocessing)
- **Disk Space**: 50GB (for models and images)

[!NOTE] Inference can be performed on CPU, but performance will be significantly slower. For production use, a GPU is highly recommended.

## Services

### 1. Handler Service (API Gateway)

**Purpose**: Main API service that receives client requests and orchestrates the processing pipeline.

**Key Responsibilities**:

- Accept HTTP requests for image generation and editing
- Validate request payloads
- Enqueue tasks to Redis
- Load and Manage feature specific style vectors

**Technology Stack**:

- FastAPI
- MongoDB async driver (motor)
- Celery (for task queueing)

---

### 2. Retriever Service (Query API)

**Purpose**: Dedicated service for retrieving generated images and metadata from storage.

**Key Responsibilities**:

- Query MongoDB for image metadata
- Retrieve images from S3
- Provide status updates on image generation status

**Technology Stack**:

- FastAPI
- MongoDB async driver (motor)
- AWS SDK (boto3)

---

### 3. Generator Service (Celery Worker)

**Purpose**: Distributed worker that generates images from latent space vectors using StyleGAN2.

**Queue**: `generation_queue` (Redis)

**Key Responsibilities**:

- Load stylegan2 generator and weights
- Generate images from S-space (style space)
- Generate images from W-space (not implemented yet)
- Upload generated images to S3
- Update MongoDB with generation results
- Handle generation failures and retries

**Technology Stack**:

- Celery
- PyTorch
- Custom CUDA operations
- TorchVision

**Key Tasks**:

- `GENERATE_S`: Generate image from style space
- `GENERATE_W`: Generate image from style space (Not implemented yet)

---

### 4. Preprocessor Service (Celery Worker)

**Purpose**: Distributed worker that handles style mixing and preprocessing operations.

**Queue**: `preprocessing_queue` (Redis)

**Key Responsibilities**:

- Mix multiple style vectors
- Seed to Style vector using the Mapper Neural Network.
- \+ More functions to be added in the future

**Technology Stack**:

- Celery
- PyTorch
- CLIP based functions (text-to-image models) (To be Implemented)

---

## Setup Instructions

### Prerequisites

1. **Install Python**

   ```bash
   # Verify Python 3.8+
   python --version
   ```

2. **Install Git**

   ```bash
   # Verify Git installation
   git --version
   ```

3. **Set up MongoDB**

   ```bash
   # Start MongoDB (local or cloud)
   # Update connection string in .env files
   ```

4. **Set up Redis**

   ```bash
   # Start Redis server (or use Redis Cloud, etc)
   # Verify connection if using local Redis
   redis-cli ping
   ```

5. **Get AWS Credentials**
    *   If using AWS S3, create an IAM user with S3 access and get the Access Key and ID.
    *   If using Minio, set up Minio server with appropriate access keys.

### Installation Steps

#### Step 1: Clone the Repository

```bash
git clone https://github.com/mind2sketch/mind2sketch-servers.git
cd mind2sketch-servers
```

#### Step 2: Set Up Handler Service

```bash
cd Handler

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create and update .env file with your configuration 
```

#### Step 3: Set Up Retriever Service

```bash
cd ../Retriever

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create and update .env file with your configuration 
```

#### Step 4: Set Up Generator Service

```bash
cd ../Generator

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For GPU support, ensure CUDA is properly set up and PyTorch is installed with CUDA support. Refer to the PyTorch installation guide for details.

# Create and update .env file with your configuration
```

#### Step 5: Set Up Preprocessor Service

```bash
cd ../Preprocessor

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create and update .env file with your configuration
```

---

## Configuration

### Environment Variables

Each service requires a `.env` file in its root directory. Create these files. Refer to the `config.py` files in each service for the required environment variables. config.py will automatically load the .env file and make the environment variables declared in uppercase inside .env  assigned to the lowercase variables specified inside itself upon service startup.


## Running the Services


#### Terminal 1 - Start Redis (If self hosting)

```bash
redis-server
```

#### Terminal 2 - Start MongoDB (If self hosting)

```bash
mongod --dbpath /path/to/data
```

#### Terminal 3 - Start Handler Service

```bash
cd Handler
.\venv\Scripts\activate
fastapi run main:app --host 0.0.0.0 --port 8000 --reload
```
[!NOTE] The Handler service must be started before the workers, as it is responsible for enqueuing tasks to Redis. Select the port for the Handler service (default 8000) and ensure that it matches the configuration in the .env files of the workers.

#### Terminal 4 - Start Retriever Service

```bash
cd Retriever
.\venv\Scripts\activate
fastapi run main:app --host 0.0.0.0 --port 8001 --reload
```
[!NOTE] The Retriever service can be started at any time, but it is recommended to start it after the Handler service to ensure that the system is fully operational. Select the port for the Retriever service (default 8001) and ensure that it matches the configuration in the .env files of the workers.

#### Terminal 5 - Start Generator Worker

```bash
cd Generator
.\venv\Scripts\activate
celery -A worker worker --loglevel=info --pool=solo
```

[!Note] pool is set to solo to avoid multiprocessing issues with CUDA. Use other options cautiously.

#### Terminal 6 - Start Preprocessor Worker

```bash
cd Preprocessor
.\venv\Scripts\activate
celery -A worker worker --loglevel=info --pool=solo
```

[!Note] pool is set to solo to avoid multiprocessing issues with CUDA. Use other options cautiously.

## Scaling for Higher Inference Throughput

Note that both the Generator and Preprocessor services can be scaled horizontally for higher inference throughput, just by starting multiple worker instances on multiple gpu servers with exact same configuration. 
