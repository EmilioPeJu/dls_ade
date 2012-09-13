#!/bin/bash
# File to interrogate the users latest build

usage()
{
    echo "Usage: $0 [-n #] [-j] [-o] [-s] [-e] [-l] [-f] [-w]"
    echo ""
    echo "  options:"
    echo "    -n # : # is a number and specifies to search for the #th last job"
    echo "    -j : Print the job file executed by the build server"
    echo "    -o : Print the job output file collected by the build server"
    echo "    -s : Print the make status (if it exists)"
    echo "    -e : Print the make error file (if it exists)"
    echo "    -l : Print the make log file (if it exists)"
    echo "    -f : Follow the make log file (if it exists)"
    echo "    -w : Wait for the build to complete"
    exit $1

}

build_num=1
job=0
out=0
status=0
errors=0
logs=0
wait=0
follow=0

while getopts 'n:joseltwfh' option; do
    case "$option" in
        n ) build_num=$OPTARG ;;
        j ) job=1 ;;
        o ) out=1 ;;
        s ) status=1 ;;
        e ) errors=1 ;;
        l ) logs=1 ;;
        f ) follow=1 ;;
        w ) wait=1 ;;
        t ) test=1 ;;
        h ) usage 0 ;;
         *) echo >&2 "Invalid option: $option"
            usage 1 ;;
    esac
done


# If this script has any argument then assume it is being tested
if (( $test )) ; then
    queue_dir=queue
    pending_dir=pending
    complete_dir=complete
else
    queue_dir=/dls_sw/work/etc/build/queue
    pending_dir=/dls_sw/prod/etc/build/pending
    complete_dir=/dls_sw/prod/etc/build/complete
fi

# Find the build we wish to know about
read -r release_dir module version jobname server <<< $(tail -$build_num ~/.dls-release-log | head -1) 
release_dir=${release_dir//\\//}
release_dir=${release_dir/W://dls_sw}

queued=$queue_dir/${jobname}.$server
pending=$pending_dir/$jobname*
complete=$complete_dir/${jobname}.$server

if [ -e $queued  ] ; then
    echo Job queued as $queued
    (( job )) && cat $queued
fi

if [ "$(echo $pending)" != "$pending_dir/$jobname*" ] ; then
    echo Job processing as $pending
    (( job )) && cat $pending
fi

if [ ! -e $complete ] ; then
    if (( $wait )) ; then
        echo "Waiting for job to complete"
        while [ ! -e $complete ] ; do
            sleep 1
        done
    elif (( $follow )) ; then
        if [ -e $complete_dir/${jobname}.out ] ; then
            tail -f $complete_dir/${jobname}.out
        else
            echo No output file to follow yet
        fi
    fi
fi

make_status=$release_dir/$module/$version/${jobname}.sta
make_errors=$release_dir/$module/$version/${jobname}.err
make_logs=$release_dir/$module/$version/${jobname}.log

if [ -e $make_status ] ; then
    echo
    echo "Make completed with status code of: $(cat $make_status)"
fi

if [ -s $make_errors ] ; then
    echo
    echo "Make errors were generated and are in: $make_errors"
    (( $errors )) && cat $make_errors
fi

if [ -s $make_logs ] ; then
    echo
    echo "Make log is in: $make_logs"
    (( $logs )) && cat $make_logs
fi

if [ -e $complete_dir/${jobname}.out ] ; then
    echo
    echo "Build job output in: $complete_dir/${jobname}.out"
    (( $out )) && cat $complete_dir/${jobname}.out
fi

if [ -e $complete ] ; then
    echo
    echo "Build job script in: $complete"
    (( $job )) && cat $complete
fi
