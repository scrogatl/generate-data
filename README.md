# generate-data
Generate data for Tanzu Observability 

----
The shell scripts send data to Tanzu Observability for demo purposes.

You'll need to assign these variables to match you situation:
* TOKEN=<API KEY HERE>
* SOURCE=<SOURCE / HOST HERE>
* URL=https://longboard.wavefront.com/report  
----

The python script will send data to Tanzu Observability to demo alerts.

```./dataload.py -i ~/demo/demo.out -t localhost -p 2878```

Where `t` is the address of a Tanzu Observability (Wavefront) proxy.

