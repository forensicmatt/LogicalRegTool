# LogicalRegTool
A registry tool that can be ran on a logical volume. JSONL output for NoSQL.

This tool utilizes the yarp (Yet Another Registry Parser) library. Special thanks to Maxim Suhanov. https://github.com/msuhanov/yarp



# Usage
```
usage: LogicalRegTool.py [-h] -s SOURCE

Process registry files from a logical volume. The output is currently in JSONL format.
This tool requires Admin privileges to open the Logical Volume.

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        Logical source [Example: \\.\C:]
```

# Plugins
| Plugin | Description | Status | Peer Reviewed |
| --- | --- | --- | --- |
| AppCompat | Parse both AppCompatFlags and AppCompatCache | In Development | No |
| Bam | Parse Bam Keys | Complete | No |
| RegistryIterater | Iterate Keys and Values | In Development | No |
| UsbEnumerator | Enumerate USB Devices | In Development | No |
| UserAssist | Parse UserAssist | Complete | No |

