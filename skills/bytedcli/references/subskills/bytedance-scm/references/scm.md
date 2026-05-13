# SCM

```bash
bytedcli scm repo list --page 1 --size 10
bytedcli scm repo search "byteapi/command/bytedcli"
bytedcli scm repo version list "byteapi/command/bytedcli" --branch master --type online --status build_ok
bytedcli scm repo version list --repo-id 533180 --branch master --type online
bytedcli scm repo build "byteapi/command/bytedcli" --branch master --type test -e '{"CUSTOM_KEY":"VALUE"}' -m "trigger build reason"
# 指定编译架构（重复或逗号分隔，仅允许 x86_64 / aarch64 / x86_64,aarch64）
bytedcli scm repo build "byteapi/command/bytedcli" --branch master --type test --arch x86_64,aarch64
# 通过 commit hash 直接打包（--commit 和 --branch 互斥，不需要指定分支，产物只在 CN CDN 落地）
bytedcli scm repo build "byteapi/command/bytedcli" --commit abc123def456 --type offline
bytedcli scm repo build --repo-id 533180 --branch master --type offline
bytedcli scm repo build-log "byteapi/command/bytedcli" "1.0.0.1686" --step building
bytedcli scm repo build-log "byteapi/command/bytedcli" "1.0.0.1686" --status failed
bytedcli scm repo build-log --repo-id 533180 "1.0.0.1686" --step building
```

## 区域同步 flag

`scm repo build` 支持 3 个同步开关，默认继承仓库配置（SCM 仓库设置页的 `sync_aws` / `sync_oss` / `sync_bvc`），CLI 可覆盖：

| Flag | 作用 | 对应 build stage |
|---|---|---|
| `--sync-aws` / `--no-sync-aws` | VA/US 区域上传 | `uploading-va-source` |
| `--sync-oss` / `--no-sync-oss` | SG/Aliyun 区域上传 | `uploading-sg-source` |
| `--sync-bvc` / `--no-sync-bvc` | BVC 多 region 发布格式 | `uploading-bvc-source` |

仅 `--branch` 模式会真正触发海外上传；`--commit` 模式产物只在 CN CDN 落地。
