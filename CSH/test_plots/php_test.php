<!DOCTYPE html>

<!--
    #################################################################################################
    #                                                                                               #
    #    msid_data_interactive.php                                                                  #
    #                                                                                               #
    #    This php script runs a python script to reate an interactive msid trend page.              #
    #    However, if it fails to create, it will dsiplay "the page is not created" notice           #
    #                                                                                               #
    #    author: t. isobe (tisobe@cfa.harvard.eud)                                                  #
    #                                                                                               #
    #    last update: Jan 31, 2018                                                                  #
    #                                                                                               #
    #################################################################################################
-->
<html>
<head>
    <title>PHP test</title>
</head>
<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FAEBD7;
font-family:Georgia, "Times New Roman", Times, serif">


<?php
   $msid_group    = $_POST['msid_group'];

/* run python script for test */

    exec("PYTHONPATH=/proj/sot/ska3/flight/lib/python3.6/site-packages  /proj/sot/ska3/flight/bin/python   /data/mta4/www/CSH/test_plots/soh_msid_plot_class.py $msid_group");


/* if the page is not created, display the "not created" notice */

    echo '<title>Page Not Created Notice</title>';
    echo '</head>';
    echo '<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FAEBD7;font-family:Georgia, "Times New Roman", Times, serif">';

    echo '<h2 style="padding-top:30px;">Sorry! The Page Was Not Created!</h2>';
    echo '<p>';
    echo 'The requested interactive page was not created. There are a few possible reasons.';
    echo '</p>';

    echo '<ol>';
    echo '    <li> The requested data are too large and the system could not handle.';
    echo '        <ul>';
    echo '            <li>You can try again; it could be the cpu is less taxed when the time you try again.</li>';
    echo '            <li>Reduce the time span and/or the sample size.</li>';
    echo '        </ul>';
    echo '    </li>';
    echo '    <li style="padding-top:20px"> There were no data in the requested period.';
    echo '        <ul>';
    echo '            <li>Although this is a less likely case, you can try to see whether the different period';
    echo '                will create the plot. If it does, please report to';
    echo '                <a href="mailto:tisobe@cfa.harvard.edu">tisobe@cfa.harvard.edu</a>.';
    echo '            </li>';
    echo '        </ul>';
    echo '    </li>';
    echo '    <li style="padding-top:20px"> The data are not in the SOT engineering database.';
    echo '        <ul>';
    echo '            <li>The interactive plot can be produced only when the data are in SOT engineering';
    echo '            database. This is the major causes of not producing the interactive plot.';
    echo '            </li>';
    echo '            <li>';
    echo '            A msid with condtions (such as HRC with HRC-I is in use) are not in the database';
    echo '            and computed data (such as HRMA computed average) are not in the database.';
    echo '            </li>';
    echo '        </ul>';

    echo '    </li>';

    echo '</ol>';
/* change the permission so that non-"http" user can delete the file */

?>


<div style='padding-top:300px'>
</div>

<hr />
<p style="text-align:left; padding-top:10px;padding-bottom:20px">
If you have any questions, please contact
<a href="mailto:tisobe@cfa.harvard.edu">tisobe@cfa.harvard.edu</a>.



</body>
</html>
