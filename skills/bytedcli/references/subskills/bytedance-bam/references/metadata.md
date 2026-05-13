# BAM 元数据管理

```bash
# PSM 列表
bytedcli bam psm list --cluster default
bytedcli bam psm search "example.service.api" --cluster default

# 方法列表 / 详情（支持 --cluster 指定集群，--version 指定版本）
bytedcli bam method list --psm "example.service.api"
bytedcli bam method list --psm "example.service.api" --cluster i18n
bytedcli bam method list --psm "example.service.api" --cluster i18n --version 1.0.155
bytedcli bam method get --endpoint-id 123456 --version 1.2.3
bytedcli bam method get --psm "example.service.api" --method "DemoMethod"
bytedcli bam method get --psm "example.service.api" --method "DemoMethod" --cluster i18n
bytedcli bam method gencode --endpoint-id 123456
bytedcli bam method gencode --psm "example.service.api" --method "DemoMethod"
bytedcli bam method gencode --psm "example.service.api" --method "DemoMethod" --schema-type response

# 版本历史
bytedcli bam version list "example.service.api" --cluster default

# 创建/更新 IDL 版本（--next-version 自动 patch +1；或 --version 指定版本号）
bytedcli bam idl update --psm "example.service.api" --branch master --next-version
bytedcli bam idl update --psm "example.service.api" --branch "codex/fix-idl" --version "1.2.4" --commit-id "abc1234" --commit-msg "update idl"
```
