# Reusable Metrics

Metrics make process learning durable. They inform Product Owner judgment but do not replace it.

## Required Metrics

| Metric | Source rule |
| --- | --- |
| Elapsed time | observed from timestamps when available; otherwise estimated |
| Agent turns | observed from conversation/ledger when available |
| Approx token use | estimated unless a tool reports it |
| Review loops | observed from review/triage records |
| High findings | observed from review records |
| Medium findings | observed from review records |
| Low findings | observed from review records |
| Human decisions | observed from explicit approvals/rejections/skips |
| QA outcome | observed from human QA result |
| Outcome | observed from final iteration status |

## Source Types

- **observed:** command output, timestamps, git history, review output, QA result, explicit human decision, current-cycle state.
- **estimated:** token use, inferred human effort, partial elapsed time, or reconstructed values.

Retrospectives must keep value, source type, and evidence separate.

