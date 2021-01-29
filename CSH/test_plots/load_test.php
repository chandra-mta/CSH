<!DOCTYPE html>

<html>
<head>
    <title>SOH Plots</title>
	
    <link rel="stylesheet" href="https://cdn.pydata.org/bokeh/release/bokeh-0.12.7.min.css" type="text/css" />
    <script type="text/javascript" src="https://cdn.pydata.org/bokeh/release/bokeh-0.12.7.min.js"></script>

	<script src="../js_snap/lib/jquery-2.2.0.js"></script>
	

</head>
<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FAEBD7;
font-family:Georgia, "Times New Roman", Times, serif">

<?php 
   $msid_group = $_POST['msid_group'];
   $myfile = "/data/mta4/www/CSH/test_plots/.plot_these.txt";
   $timestamp = time();
   $text = $msid_group." ".$timestamp."\n";
   file_put_contents($myfile, $text, FILE_APPEND | LOCK_EX);
   chmod(".plot_these.txt", 0666);
?>

<div id="plot"><b> 
Hello
Your plot is loading, it may take a few seconds<br>
Up to 15 seconds, the first time around</b></div>

<button type="submit" onClick="refreshPage()">Refresh Plot</button>

<script> $("#plot").load("plot.php", {'msid_group':'<?php echo $_POST['msid_group']; ?>'}); </script>
<script> function refreshPage(){ window.location.reload();} </script>

</body>
</html>
