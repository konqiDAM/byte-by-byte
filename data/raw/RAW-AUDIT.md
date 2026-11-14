# Raw artefact audit

Hashes and cross-checks for everything in `data/raw/`. Regenerate with
`python tools/audit_raw.py .`; the machine list is `data/raw/manifest.csv`.

## Files

| path | bytes | sha256 (first 16) | what it is |
|---|---|---|---|
| `data/raw/docs/AGENT_UPDATE_2026-11-13.md` | 7377 | `6f09d9f310817267` | the brief handed to every agent (includes two refuted laws) |
| `data/raw/docs/CLOSED.md` | 23074 | `14766d8a7ce21d30` | the proved walls, human view |
| `data/raw/docs/INDEX.md` | 110874 | `1317099fe181f327` | every address touched: status, best residue, file, handoff |
| `data/raw/docs/LOCAL_MODEL_TASK_0x00501250.md` | 11496 | `ea39ecd3b1a5818e` | self-contained task for a local model |
| `data/raw/docs/NEAR_MISSES.md` | 3782 | `65a107bb9772b7e8` | open near misses at residue <= 10 |
| `data/raw/docs/SESSION_CLOSE_6_2026-11-13.md` | 8606 | `3f478df038238246` | state + strategy ledger, evening |
| `data/raw/docs/SESSION_CLOSE_7_2026-11-13.md` | 5799 | `6361d0400fca69ce` | state + strategy ledger, night (the twin strategy) |
| `data/raw/docs/TRAPS.md` | 9866 | `67f4af39daa0e70f` | strike risks, tool traps, cost traps |
| `data/raw/docs/_big_twin_pool.json` | 1346 | `95585eedb5b2b62f` | the big (>=1 KB) twin pool as scanned |
| `data/raw/docs/_closed.txt` | 22657 | `4ec759153750cc6c` | the same walls, machine copy (address<TAB>reason) |
| `data/raw/docs/_twin_candidates.json` | 6207 | `50281ae96cd77317` | open twin-bearing candidates, with confidence and give-up counts |
| `data/raw/docs/lessons-rival-code.md` | 450369 | `11ad282129600f43` | the law book - every lever and wall with the measurement behind it |
| `data/raw/docs/sessions.md` | 248105 | `53b9eefdf4eebf1d` | the subagent registry: one row per launch, with session id, claim, model, purpose, status, outcome |
| `data/raw/handoffs/0x00409a80.md` | 5545 | `f14af1642bea0fae` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0041a300.md` | 6946 | `e88ac5b728e2ce94` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00421e00.md` | 1839 | `51b32353192f4000` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004224d0.md` | 6484 | `aa749e9a716fff7c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0042e4f0.md` | 4159 | `dec590e5db962e51` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00437dc0.md` | 12501 | `c85df0a8cc3c4751` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0043eb00.md` | 13842 | `de82fdbaeea8c1e6` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00445190.md` | 6900 | `0947cf1ee50b3c9b` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00445f50.md` | 1898 | `283f51a707f5674d` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0045a060.md` | 7646 | `8ea91ed480dc9539` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0045add0.md` | 13807 | `2f05af3f10756b96` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0045feb0.md` | 7724 | `c3ff034f9c2437d8` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00473360.md` | 18100 | `53e113a3610b6b5c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0047ff70.md` | 6641 | `ab2149bc06651e14` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0049e490.md` | 7359 | `f07b1469f635b631` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0049fb90.md` | 1223 | `6b8f9cd7490d693e` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004a21b0.md` | 5428 | `fb0f89bc1622e0ef` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004dade0.md` | 9649 | `429b54dc1a83da45` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004daff0.md` | 6954 | `7e3706e3b9e52730` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004e0b30.md` | 10038 | `ac08b167a6d0c72c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004ea010.md` | 5178 | `20d54363d30d52fd` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004edf90.md` | 7310 | `0219956a218dbedd` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004f2df0.md` | 7018 | `879bee3f63ac85d1` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004f31a0.md` | 9270 | `a0d0398f9ab3de1a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x004f5f00.md` | 19094 | `400a0459de83809a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00500680.md` | 2744 | `67d5891e23fb2f0f` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00502930.md` | 6299 | `968c5eb291f394e7` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0051d140.md` | 5792 | `477742c11331cbba` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00540c50.md` | 10723 | `2137f5d119781061` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00540f60.md` | 15845 | `be7a9e0989d070c9` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005423d0.md` | 4614 | `e9868a3385b891fa` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00555870.md` | 8626 | `881cb3228cf94d23` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0055e990.md` | 5298 | `3714c34854b7d4da` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005619e0.md` | 7109 | `1a0a554385cbeb81` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00564cd0.md` | 6190 | `f2a9f8a751f95591` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005693d0.md` | 17396 | `99ad86efdbcc1536` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00569f30.md` | 3153 | `cd757cd85ba2e9a1` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00575a30.md` | 12335 | `06b15670d501bff1` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0058e230.md` | 9372 | `a821eaa7ed02f713` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0059ed00.md` | 8372 | `14c05e34d811ebde` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005ae7e0.md` | 8703 | `dc9ddcfc8fdef2f1` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005b7c10.md` | 7907 | `d7a7665fab35f754` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005bf4b0.md` | 2396 | `cca037e26121d90f` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005d79d0.md` | 2267 | `f9eefb0f67a48683` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005d8840.md` | 5420 | `ab33f3ee72037a24` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005d91a0.md` | 15672 | `9c3ae8070ea472e8` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x005efdd0.md` | 2637 | `a84ed3c7adc75022` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00600750.md` | 7705 | `88eaac889185329a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00613450.md` | 11727 | `31158715ec2e85d7` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00615e50.md` | 6138 | `d1e63dea7feeacc4` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0061bd10.md` | 30906 | `6a7a1c0904012d89` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0063bad0.md` | 5180 | `176e72ab41f62508` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0063ce90.md` | 1049 | `5cc365678cb6d0b3` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0063e730.md` | 3384 | `04e9c600f8c3d37d` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006404e0.md` | 9712 | `478e521420388eb5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00643540.md` | 5064 | `0fc2fda7edbd8478` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0065a920.md` | 9758 | `fc52dd261842ed9c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0065e9f0.md` | 19365 | `df536deed6bc030f` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0066ab70.md` | 2306 | `c450dfcdfe5394b5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0066c330.md` | 7402 | `bfa3e002b714680c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0066e7b0.md` | 7020 | `1f346a020cf8646e` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00673c40.md` | 11926 | `158b7e79fe29378a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006a13f0.md` | 5765 | `1d3475329566e0a7` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006a1bf0.md` | 4534 | `caccd96561f0a620` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006ae220.md` | 5361 | `e0dbb23bd14b30b5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006b5dd0.md` | 10875 | `6a2b63cec2d9762b` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006b61b0.md` | 7983 | `55517f921dd4d33b` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006c53a0.md` | 8779 | `fb597e3cd846e4d4` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006cd660.md` | 7168 | `e875750776164951` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006d08a0.md` | 5871 | `1cc0bfc3fd721fd8` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006e9ba0.md` | 3059 | `fa264cdc5fcfc287` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x006fb820.md` | 2169 | `94d6b46269946948` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00701f00.md` | 2447 | `037ba3ba3475ffd2` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00702430.md` | 9252 | `e42c960d88b55976` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00703c20.md` | 831 | `d358e52a848a48c0` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007078d0.md` | 5331 | `6f437e598da105c1` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00707af0.md` | 14230 | `19e0839a7f387ab3` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00709320.md` | 996 | `3f3462827ae160e4` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0070a9a0.md` | 5105 | `5982e30014c1d756` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0070dd00.md` | 6714 | `ea3a181cb54b6cde` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00711660.md` | 4713 | `4c834758d69e306b` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00716d90.md` | 3737 | `6508c07e353c9a68` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00718f00.md` | 6319 | `46964786d34b1cd0` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0073e740.md` | 7644 | `458a31bd20ba8302` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0073f7f0.md` | 7764 | `69ccd1a5477fb6a5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00742370.md` | 3020 | `90d70f276f6a9ebb` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00742da0.md` | 12372 | `c8cf9da30241c916` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00742df0.md` | 8107 | `21c5bf10f77ac9f6` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00757ce0.md` | 8054 | `ac630102c21fbf9f` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00762ab0.md` | 11452 | `a6623f891b2eae59` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00763190.md` | 14840 | `cdc78b92be376509` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007641c0.md` | 15322 | `b10ba36b677a134c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00769230.md` | 10917 | `02e20b17e408256f` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00771a40.md` | 4545 | `8d1c3ca8df42c07a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0078ed50.md` | 5939 | `d5b570d487ef5b45` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00794740.md` | 10893 | `d423a8eca47f56e8` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007b5d70.md` | 1528 | `7ac4a429e53b987a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007b8510.md` | 8239 | `3de8f0712e19c569` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007ca970.md` | 3141 | `5c5d6eb4f272fc43` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007d1ae0.md` | 5915 | `7c84b95d3c5d4ef1` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007d53c0.md` | 13674 | `d15d9d83f09ffcf5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007d6300.md` | 3896 | `79108c6a1d7cf819` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007dab90.md` | 7621 | `eda432546069f662` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x007e2bb0.md` | 6904 | `1a5ab17c68c567a5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0086c3e0.md` | 2258 | `153a84a2ba4a7ac4` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00881790.md` | 5993 | `f74f85becd62eb4a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x008899e0.md` | 2990 | `f7a78047e692805a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x008d7020.md` | 8120 | `4a4fbc6020ebb3c1` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x008e4d50.md` | 13692 | `343ad4683a0da7fa` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x008efb10.md` | 8108 | `b52f34ec9ab38c85` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x008fb0b0.md` | 6783 | `7c311eb5671df0b7` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x008fb4e0.md` | 4988 | `410788a42d582a07` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00902620-analysis.md` | 55186 | `d5236d2dad625424` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00902620.md` | 6598 | `e0a30cc653ae2483` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009035e0.md` | 13416 | `f232e88a5a10aa24` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00904da0.md` | 6928 | `f5a17324d45a89ff` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00906740.md` | 2455 | `9f1f818819921241` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0090d6b0.md` | 7028 | `8c179c5ab3c1f178` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0090d750.md` | 9561 | `836084b545dac2bc` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00916290.md` | 3390 | `dc9a8c9b0ecd08f0` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00918e70.md` | 23603 | `827d12b01524a3c3` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0091e6a0.md` | 13357 | `086f0c730f780871` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00925970.md` | 4051 | `dc0bbaaa921da858` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00927640.md` | 7244 | `56af3dccf993456a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0092a1a0.md` | 1348 | `b1c25f5c7435742c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0092e990.md` | 6339 | `647054c8258a0ecb` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0092f990.md` | 5850 | `4d77afeae99c7454` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00930430.md` | 3721 | `ad14ce14de4265cb` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00931eb0.md` | 11693 | `2857e93b60d856ae` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009550e0.md` | 36234 | `c07fa63f2a189ff0` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00955810.md` | 9746 | `8acf595d9a30aaaf` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00961300.md` | 6916 | `560218c98ee9cabc` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0096fa60.md` | 5314 | `ca22334aa1930cef` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0097aa70.md` | 6612 | `6ddc48bd55cce01a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x0098df40.md` | 14997 | `5f0a8a2c96fef3eb` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009925d0.md` | 4583 | `ece0d6bd125b327d` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00994580.md` | 7821 | `521adb77b7743783` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00998850.md` | 6581 | `4792b0f75629386b` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009a9cb0.md` | 2636 | `ff9f3e016edbbb44` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009bb7d0.md` | 7413 | `406b4ec76afd53a0` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009bcad0.md` | 5942 | `eee7ade738f7e2ba` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009bf5c0.md` | 4189 | `8f12291dd45e53a0` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009c7730.md` | 5279 | `85fa6209ae80a3eb` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009dbf00.md` | 2578 | `2a0aae14089712f2` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009e4ef0.md` | 6474 | `482132614690393d` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009e8450.md` | 1294 | `174560bd856bc663` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009e9c60.md` | 7981 | `c3ac43ac9ddb13d1` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x009f9800.md` | 10789 | `d6bffbffb836de24` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a0b990.md` | 6268 | `dea5112f4cf707ec` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a24db0.md` | 10809 | `6270c9b5eeed3393` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a29960.md` | 10874 | `8a4326305fb5b737` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a3ab70.md` | 3852 | `3d8109be9fed97b5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a42140.md` | 6533 | `0d4c07be357cc5b8` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a485f0.md` | 10582 | `c9dc8af70950c1b3` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a485f0_prev.md` | 5790 | `4efa42471dd508a6` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a4e670.md` | 4775 | `2b3f73aac983b472` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a560b0.md` | 3296 | `1b7ab412433d3cf2` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a564b0.md` | 5215 | `cc8860fcdc0b3723` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a5b5d0.md` | 14811 | `3d34c21b192935aa` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a68fc0.md` | 4713 | `c050b5d94332d3ab` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a6d020.md` | 7306 | `dfa9f6a4f517472a` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a6ddd0.md` | 8722 | `df1c40549d6c3667` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a77840.md` | 6511 | `9d45df45c218c20b` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a7e010.md` | 952 | `dd72ad547130ad00` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a88610.md` | 7223 | `84ca73693cd782e5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a89680.md` | 7547 | `fb57a44dd51fcba5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00a8d760.md` | 14023 | `0efba5af2c5831ec` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00aa31d0.md` | 11650 | `0336f6eda2d5a6cd` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00aa5870.md` | 6592 | `404bc0f735c7fea2` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00ac4900.md` | 1532 | `f3d5901d2f8dddb0` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00b40790.md` | 4210 | `cf447f540cc8cae7` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00bb9260.md` | 7465 | `592f86b35dc8c7e6` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00bcb4c0.md` | 6636 | `27af1c8aa498569f` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00bd20f0.md` | 5093 | `778dadaf65efb18c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00bd8f90.md` | 11651 | `d310f64123de1dca` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00bf6260.md` | 13051 | `795057e3239cc90c` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00bf7520.md` | 5340 | `4c25ceaa39ac3774` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00c01530.md` | 1899 | `8bdd2beb781a94f5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00c05bef.md` | 2810 | `457c755eae253a80` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/handoffs/0x00c1059e.md` | 10771 | `11f81c420087afe5` | handoff for one function: what was tried, what it leaves behind |
| `data/raw/tools/add_sessions.py` | 594 | `f4523f154129bc70` | analysis tool |
| `data/raw/tools/asm3.py` | 3549 | `83e89727fcc0f3ed` | analysis tool |
| `data/raw/tools/audit_banked_open.py` | 5268 | `810c43b94f8b5e7d` | analysis tool |
| `data/raw/tools/build_index.py` | 8182 | `c876f9aca4694ce6` | analysis tool |
| `data/raw/tools/capture_409.py` | 2210 | `6db4f18d7c38458b` | analysis tool |
| `data/raw/tools/claim_many.py` | 1563 | `e0d29250bfb1c0f3` | analysis tool |
| `data/raw/tools/closed_list.py` | 4836 | `7906e849aeb248ec` | analysis tool |
| `data/raw/tools/fetch_pack.py` | 2101 | `ddf5835a2be7afc8` | analysis tool |
| `data/raw/tools/harvest_zero_drafts.py` | 5909 | `94d23ab18501c594` | analysis tool |
| `data/raw/tools/prologue_probe.py` | 2408 | `5612bef5f057074d` | analysis tool |
| `data/raw/tools/refresh_409.py` | 4270 | `e17534b4e4ffa400` | analysis tool |
| `data/raw/tools/release_triaged.py` | 3768 | `d4926ccbfaf328fa` | analysis tool |
| `data/raw/tools/rescore_flags.py` | 3816 | `e1239d89000703b6` | analysis tool |
| `data/raw/tools/rescore_nearmiss.py` | 6080 | `8c644febd1b2e610` | analysis tool |
| `data/raw/tools/resubmit_banked.py` | 3882 | `d1fe4ce1e0821783` | analysis tool |
| `data/raw/tools/score_pack.py` | 2629 | `a88acc3653b28bd4` | analysis tool |
| `data/raw/tools/session_audit.py` | 6177 | `f9536acadfab7c7f` | analysis tool |
| `data/raw/tools/triage_twins.py` | 3047 | `7ee00391153c4caf` | analysis tool |
| `data/raw/tools/twins_extract.py` | 5242 | `bc8aea422a996357` | analysis tool |

## Consistency checks

| quantity | value | source |
|---|---|---|
| addresses in INDEX.md | 2044 | `docs/INDEX.md` |
| INDEX status counts | {'MATCHED': 488, 'attempted': 117, 'CLOSED': 86, 'claimed': 1353} | `docs/INDEX.md` |
| proved walls | 110 | `docs/_closed.txt` |
| law sections | 238 | `docs/lessons-rival-code.md` |
| session registry rows | 262 | `docs/sessions.md` |
| handoff files | 180 | `docs/handoffs/` |
| analysis tools | 19 | `docs/tools/` |
| candidate files | 459 | `candidates/` |
| sessions in sessions.csv | 376 | `data/sessions.csv` |
| models in model-summary.csv | 17 | `data/model-summary.csv` |

## What the audit says

* **376 sessions** in the project directory, totalling **283 hours of session wall-clock** (sum of session lifetimes - sessions overlap, so this is concurrency, not elapsed time).
* `opencode-go/deepseek-v4.1-flash#high` - 263 sessions, 252.2 h, 80,620,713 tokens in / 9,439,545 out
* `opencode/glm-5.3-flash-free#high` - 1 sessions, 8.2 h, 196,966 tokens in / 7,570 out
* `opencode-go/glm-5.3-flash#max` - 7 sessions, 4.5 h, 2,609,336 tokens in / 160,780 out
* Cost recorded by the harness is **$0.00** for every model: the work ran on subscription-style accounts (`opencode-go`), so the real constraint was never money - it was **quota windows** and **leases**.

## What was deliberately left out

No game binary, no `.obj`, no build output and no credential. The files under `data/raw/` are the working record: our own drafts, measurements and analysis. Other contributors' attempts are referred to by checkpoint id and score; where an instruction or two is quoted it is for comparison, not as a source.
