---
title: A computer model of memory rhythms and brain stimulation
short: A simulated slice of the brain's memory centre, used to ask when an electrical pulse can restart the rhythms that memory depends on.
period: 2020 to 2024 (Ph.D.)
place: Institute of Neurodegenerative Diseases (CNRS), University of Bordeaux, with Fabien Wagner and Nicolas Rougier
role: First author. Built, ran and analysed the model.
status: Published in eLife (2024)
data: Computer simulations (Python, Brian2)
current: false
order: 4
---

## The question

The hippocampus, the brain's memory centre, runs on rhythms. A slow beat called theta, a few times per second, carries faster bursts called gamma, and this pairing is closely tied to forming memories. In memory disorders these rhythms weaken. Electrical stimulation might restore them, but when should the pulse arrive, and does the timing matter?

## What I built

A computer model of a slice of the hippocampus and its neighbouring areas, made of thousands of simulated neurons. The slow theta beat comes from a group of coupled "clocks" that can be nudged and reset, much like the real pacemaker cells that drive it. Stimulation is delivered as short electrical pulses to one area.

The model builds on Amélie Aussel's detailed model of the hippocampal formation ([Aussel et al., 2018](https://pubmed.ncbi.nlm.nih.gov/30382451/)), which I adapted and extended with the pacemaker and stimulation. I am grateful to Amélie for her work and for her help throughout the development.

{% assign fig = site.static_files | where: "path", "/assets/img/elife-87356-fig1.jpg" | first %}
{% if fig %}
<figure>
  <img src="{{ '/assets/img/elife-87356-fig1.jpg' | relative_url }}" alt="Figure 1 from the eLife paper: the structure of the hippocampal model">
  <figcaption>Figure 1 from Vardalakis et al., eLife 2024 (CC BY 4.0).</figcaption>
</figure>
{% else %}
The model's structure is shown in [Figure 1 of the paper](https://elifesciences.org/articles/87356/figures#content).
{% endif %}

## What it showed

- The model produces the theta and gamma rhythms, and the way they lock together, as seen in real recordings.
- Under the right conditions a single pulse can switch the network from quiet to a self-sustaining rhythm.
- Whether the timing of a pulse matters depends on how easily the slow beat can be reset. When it resets easily, timing hardly matters; when it does not, pulses timed to the peak of the rhythm work best.
- When the rhythm is weak, a short train of pulses at the theta pace brings it back across the whole network.

The practical upshot: closely timed, "closed-loop" stimulation is most worth the effort in brains where the rhythm does not reset easily.

## Output

- Vardalakis N., Aussel A., Rougier N.P., Wagner F.B. [A dynamical computational model of theta generation in hippocampal circuits to study theta–gamma oscillations during neurostimulation](https://doi.org/10.7554/eLife.87356). *eLife* (2024).
- Built on: Aussel A., Buhry L., Tyvaert L., Ranta R. [A detailed anatomical and mathematical model of the hippocampal formation for the generation of sharp-wave ripples and theta-nested gamma oscillations](https://pubmed.ncbi.nlm.nih.gov/30382451/). *Journal of Computational Neuroscience* 45 (2018).
- Code: [github.com/NikVard/memstim-hh](https://github.com/NikVard/memstim-hh)
- Presented at the FENS Forum (2022) and the Deep Brain Stimulation Society congress (2023).
