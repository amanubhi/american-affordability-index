# Publication record

Public Sites deployment and GitHub publication are verified. The initial release passed a full clean-environment CI rebuild.

- Public repository: https://github.com/amanubhi/american-affordability-index
- Site project: appgprj_6ad66cb9b5a8819186fb78b44678327c
- Site version 1 source commit: 556c6a818fa04d9de719e43ccecf1a33042bb2bf
- Saved version: appgprj_6ad66cb9b5a8819186fb78b44678327c~appgver_89a29c93b988819190dd1d7e177b7f17
- Deployment: appgdep_6ad67037e23c8191b2f4d32a58acf1ed
- Audience explicitly set to public for the requested public dashboard.
- No live browser visual inspection occurred; the browser approval gate declined localhost access. See VALIDATION.md.

- Verified native Sites status: succeeded, October 19, 2026, 19:32:23 UTC.
- Public URL: https://american-affordability-index.sunlittuna11.chatgpt.site
- Implementation: browser-only companion. Streamlit is separately runnable from app.py.

## Final public Site version

- Version: 2
- Pushed Site source commit: f09ce10592434e5931b35520c1b10fc1acf69440
- Saved version: appgprj_6ad66cb9b5a8819186fb78b44678327c~appgver_ed71119f43888191b8ed05f7bd94d001
- Deployment: appgdep_6ad670ff0d248191948921088887cd31
- Native status: succeeded, October 19, 2026, 19:35:34 UTC.
- Version 2 aligns the packaged data order with the final deterministic pipeline export.

## GitHub release and CI

- Public repository: https://github.com/amanubhi/american-affordability-index
- Default branch: codex/initial-release
- Initial release commit: 84a6131492d9805af20affa60e00b1001deaabd5
- Clean-environment run: https://github.com/amanubhi/american-affordability-index/actions/runs/39312426715
- Result: succeeded. Dependency installation, full offline pipeline with storytelling, six JS cases, 24 Python tests and artifact upload all passed in 54 seconds.
- GitHub emitted nonblocking action-runtime/runner-migration annotations. They did not prevent the validated build.
- The follow-up documentation/chart-label correction is validated by the subsequent commit's workflow.

No Streamlit server is hosted by Sites. The public deployment is the generated browser-only companion. The four-page Streamlit app is tested and included in the repository for local or separate Community Cloud deployment. No paid hosting, scheduled refresh or LinkedIn posting was performed.
