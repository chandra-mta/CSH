<!DOCTYPE html>

<html>
<head>
    <title>SOH Plots</title>
    <!--Ensure used of current package version is hosted on CDN, otherwise update-->
    <link rel="stylesheet" href="https://cdn.pydata.org/bokeh/release/bokeh-3.6.2.min.css" type="text/css" />
    <script type="text/javascript" src="https://cdn.pydata.org/bokeh/release/bokeh-3.6.2.min.js"></script>

	<script src="../js_snap/lib/jquery-2.2.0.js"></script>
	

</head>
<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FAEBD7;
font-family:Georgia, "Times New Roman", Times, serif">


<div id="plot"><b> 
Hello
Your plot is loading, it may take a few seconds<br>
Up to 15 seconds, the first time around</b></div>

<button type="submit" onClick="refreshPage()">Refresh Plot</button>

<script> $("#plot").load("plot.php", {'msid_group':'<?php echo $_POST['msid_group']; ?>'}); </script>
<script> function refreshPage(){ window.location.reload();} </script>

</body>
</html>
