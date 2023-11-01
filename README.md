# Zero-Shot Stochastic Byte Generator

![Youtube](https://github.com/nxfi777/ZSSBG/assets/127808926/db713455-d330-448c-abd8-911d0f8f3841) [Video Demo](https://youtu.be/0od-NuK8J6Y)

## Overview
This project explores the capacity of Large Language Models (LLMs), namely OpenAI's fast and capable gpt-3.5-turbo, to serve as a compelling substitute for conventional sources of randomness. The objective is to determine how effectively these AI models can rival both true random (derived from quantum events) and traditional algorithm-driven pseudo-random integer sequences. 

The solution is housed within a Docker container for simplicity of deployment, ensuring continuity across diverse computing environments.

## Model-Driven Randomness
By introducing a straightforward zero-shot prompt -- `“Choose either 0 or 1. Your choice must only contain the output.”` -- to the model, we can generate random bits. These are concatenated into bytes and converted to decimal integers. By testing the output sequences with the Wald-Wolfowitz runs test for non-randomness, we can determine whether the process is deterministic. So far, my results are inconclusive. However, the premise of the project is as follows: _Given an system capable of making a choice, and a recursive output, is the lack of memory of prior decisions equivalent to a quantum-state?_ If so, then the only inhibiting factor to true randomness in this application is the models 0/1 output weights.

## Infrastructure
Parallel processing is used for efficiency and speed in the byte generation. An issue with this is that the execution tends to 'hang' occasionally (most likely due to OpenAI's server-side handling, network latency, and race conditions). I have somewhat mitigated the problem with timeout handling and thread-locking. In cases of exceptions during requests, exponential backoff is done to try and recover any failed requests.

## Setup and Usage
1. Clone the repository:
```sh
git clone https://github.com/nxfi777/ZSSBG.git
```

2. Modify the 'Dockerfile', add your OpenAI API key:
```dockerfile
ENV OPENAI_API_KEY='< YOUR OPENAI API KEY HERE >'
```

2. Navigate to the project directory, and build with docker:
```sh
docker build .
```

3. Check for docker image ID:
```sh
docker images
```

You should have an ouput like so:
```sh
REPOSITORY                             TAG       IMAGE ID       CREATED          SIZE
<none>                                 <none>    470c7b2a3226   28 minutes ago   376MB
```

4. Run docker image:
```sh
docker run --rm 470c7b2a3226
```

where `470c7b2a3226` is the associated image ID.

## License
ZSSBG is subject to an MIT license 👍
