---
title: Reading OCD symptom states from inside the brain
short: Recording brain activity at the bedside while people with severe OCD face their triggers, and teaching a computer to tell, from those signals alone, when symptoms flare.
period: 2024 to present
place: Halpern Lab, Department of Neurosurgery, University of Pennsylvania
role: Co-first author. Data collection at the bedside, experiment design and analysis.
status: 'Preprint on <a href="https://doi.org/10.64898/2026.10.19.26365556">medRxiv</a> (2026)'
data: Recordings from electrodes placed inside the brain (stereo-EEG), plus heart rate and other body signals
current: true
order: 1
---

## The question

Deep brain stimulation, a kind of pacemaker for the brain, can help people whose obsessive-compulsive disorder has not responded to any other treatment. Today it runs at a fixed setting all day. A smarter device would turn up only when it is needed. For that, it has to recognise from brain activity alone when someone is struggling.

## What we did

Some patients spend several days in hospital with thin recording electrodes placed in the brain as part of their care. During that time we ran "naturalistic" provocation sessions: patients were gently exposed to their own real-life triggers, and at other times to neutral material, while rating how distressed they felt.

I collected these recordings at the bedside, using research recording software (BCI2000) and medical-grade amplifiers (g.tec), alongside heart rate and other body signals. I adapted existing behavioural tasks to suit each patient and ran the sessions with them.

<figure class="illus">
  {% include illustrations/ocd-decoding.svg %}
  <figcaption>Brain signals get busier when a patient faces a trigger, and the decoder's running guess follows. Illustration with made-up signals, not study data.</figcaption>
</figure>

## What I built

From the recordings I extracted the strength of brain rhythms at different frequencies and trained machine learning models to read them. The pipeline is designed for the small, precious datasets of clinical research: each patient's data stays together when the model is tested, so it is always judged on data it has never seen, and every result is checked against chance.

## Highlights

- From brain activity alone, the models tell apart moments when a patient is being actively provoked from neutral moments.
- They also track how distressed the patient says they feel, and they work on very short windows of two seconds as well as on whole one-minute periods. That is fast enough to matter for a device that adapts in real time.
- I have extended the approach from the first patients who enrolled in our study to the full group that is actively growing.

<p class="technical"><strong>For technical readers.</strong> Spectral features from stereo-EEG, decoded with regularized logistic regression under patient-grouped cross-validation, with permutation testing and false-discovery-rate control. Both provocation versus neutral and patient-reported distress (visual analogue scale) were decoded on 2-second windows and on 1-minute epochs, with AUROC up to 0.9.</p>

## Related

- Seilheimer R.L., Vardalakis N., et al. [*Patient-specific subnetwork connectivity predicts deep brain stimulation response in obsessive-compulsive disorder.*](https://doi.org/10.64898/2026.10.19.26365556) medRxiv preprint, 2026.
- Companion project: [spotting distress from frontal brain rhythms]({{ '/projects/ocd-frontal-biomarkers/' | relative_url }}).
