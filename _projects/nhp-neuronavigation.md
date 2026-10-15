---
title: Precise brain implants and memory stimulation in monkeys
short: Making deep brain implants more accurate, then testing how stimulating the memory centre affects memory and how stimulation travels through the brain.
period: 2020 to 2024 (Ph.D.)
place: Institute of Neurodegenerative Diseases (CNRS), University of Bordeaux, with Fabien Wagner
role: Navigation testing and surgical pipeline; recording experiments, hardware and analysis
status: Navigation study published (Journal of Neural Engineering, 2025). Memory study submitted.
data: Recordings from the brain surface (ECoG) and from deep electrodes in non-human primates
current: false
order: 5
---

## Getting electrodes to the right place

To study stimulation of the hippocampus, deep in the brain, the electrodes first have to land exactly on target. We found that a widely used surgical navigation system, which tracks the surface of the head, was not accurate enough for this. It works well for targets near the surface, such as for TMS, but small errors at the skull grow the deeper you go: a tiny tilt at the surface becomes millimetres of error at a deep target.

<figure class="illus">
  {% include illustrations/nhp-depth.svg %}
  <figcaption>Why depth is unforgiving: the same small tilt at the skull misses by more the deeper the target. Schematic, not to scale.</figcaption>
</figure>

We tested a navigation setup that uses several cameras to track the surgical tools, and built a step-by-step pipeline around it to guide deep implants more accurately.

## Does stimulating the memory centre change memory?

With electrodes in place, we stimulated the hippocampus and the neighbouring entorhinal area, using two different stimulation patterns, while the animals performed a memory task. Memory was disrupted while stimulation was on, and the effect did not last beyond the stimulation period.

## How stimulation travels through the brain

I also studied how signals spread between brain areas:

- Touch-like signals: a mild pulse to a nerve in the arm or tail of the monkey, recorded at the brain surface and in deep electrodes under anaesthesia.
- Single pulses delivered deep in the memory centre, and the responses they produced across the brain's surface.

Stimulating and recording on the same equipment can swamp the recording, so I built an adapter that keeps the stimulation contacts separate from the amplifier. The responses grew in size with the strength of the stimulation.

## Output

- Gupta A., Boissenin A., Vardalakis N., et al. [High-accuracy electrode implantation in deep brain structures using multi-camera neuronavigation in non-human primates](https://doi.org/10.1088/1741-2552/ae135b). *Journal of Neural Engineering* (2025).
- Boissenin A., Gupta A., Taillade M., Vardalakis N., et al. *Electrical stimulation of the hippocampus and entorhinal area transiently disrupts associative memory in non-human primates.* Submitted.
