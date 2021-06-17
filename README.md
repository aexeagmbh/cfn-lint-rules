cfn-lint-ax
===========

[![Testing](https://github.com/aexeagmbh/cfn-lint-rules/actions/workflows/tests.yml/badge.svg)](https://github.com/aexeagmbh/cfn-lint-rules/actions/workflows/tests.yml)
[![PyPI version](https://badge.fury.io/py/cfn-lint-ax.svg)](https://badge.fury.io/py/cfn-lint-ax)

Additional rules for [cfn-lint](https://github.com/aws-cloudformation/cfn-lint).

Installation
------------

```bash
pip install cfn-lint cfn-lint-ax
```


Usage
-----

```bash
cfn-lint template.yaml -a cfn_lint_ax.rules
```


Run Tests
---------
```bash
docker-compose build --pull
docker-compose run --rm rules
```


User Rules (E9XXX)
------------------

### Basic Template Errors (E90XX)

### Functions (E91XX)
* E9101 UnresolvedObject

### Parameters (E92XX)

### Resources (E93XX)
* I9301 EcsServiceFargatePlatformVersionNotOutdated
* W9301 S3BucketPublicAccess
* W9302 S3BucketEncryption
* W9303 CloudfrontDistributionLogging
* W9304 CloudfrontDistributionComment
* W9305 CertificateManagerCertificateNameTag
* W9306 CodeBuildProjectCloudWatchLogs

### Metadata (E94XX)
* E9401 MetadataAxChangesetAutoApprove

### Outputs (E96XX)

### Mappings (E97XX)

### Conditions (E98XX)
