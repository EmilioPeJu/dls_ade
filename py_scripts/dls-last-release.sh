#!/bin/bash
# Script to interrogate the users latest build

usage()
{
    cat <<EOF
Usage: $0 [-n #] [-u user] [-j] [-o] [-s] [-e] [-l] [-f] [-w] [-q] [-h]

  options:
    -n #    : # is a number and specifies to search for the #th last job
    -u user : Look at the last jobs for the specified user
    -j : Print the job file executed by the build server
    -o : Print the job output file collected by the build server
    -s : Print the make status (if it exists)
    -e : Print the make error file (if it exists)
    -l : Print the make log file (if it exists)
    -f : Follow the make log file (if it exists)
    -w : Wait for the build to complete
    -u user : Run the 
    -q : Quiet mode - suppress the job summary information
    -h : Print this message
EOF
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
suppress=0
user=$USER

while getopts 'n:u:joselfwqth' option; do
    case "$option" in
        n) build_num=$OPTARG ;;
        u) eval user=~$OPTARG ;;
        j) job=1 ;;
        o) out=1 ;;
        s) status=1 ;;
        e) errors=1 ;;
        l) logs=1 ;;
        f) follow=1 ;;
        w) wait=1 ;;
        q) suppress=1 ;;
        t) test=1 ;;
        h) usage 0 ;;
        *) echo >&2 "Invalid option: $option"
           usage 1 ;;
    esac
done


# For test mode use local directories
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
read -r release_dir module version jobname server <<< $(tail -$build_num $user/.dls-release-log | head -1) 
release_dir=${release_dir//\\//}
release_dir=${release_dir/W://dls_sw}

queued=$queue_dir/${jobname}.$server
pending=$pending_dir/${jobname}.bat
[ -e $pending ] || pending=$pending_dir/${jobname}.$server
complete=$complete_dir/${jobname}.$server
output=$complete_dir/${jobname}.out

case "$(echo $jobname | cut -d_ -f4)" in
    tools)
        if [ "${server:0:7}" == "redhat5" ] ; then
            build_dir=$release_dir/RHEL5/build_scripts/$module
        else
            build_dir=$release_dir/${server/redhat/RHEL}/$module/$version
        fi
        ;;
    python)
        if [ "${server:0:7}" == "redhat5" ] ; then
            build_dir=$release_dir/$module/$version
        else
            build_dir=$release_dir/${server/redhat/RHEL}/$module/$version
        fi
        ;;
    etc)
        build_dir=$release_dir/$module
        ;;
    *)
        build_dir=$release_dir/$module/$version
        ;;
esac

if [ -e $queued  ] ; then
    job_status=queued
    status_dir=/dls_sw/work/etc/build/queue
elif [ -e $pending ] ; then
    job_status=pending
    status_dir=/dls_sw/prod/etc/build/pending
elif [ -e $complete ] ; then
    job_status=complete
    status_dir=/dls_sw/prod/etc/build/complete
else
    echo "ERROR: No job information found"
    exit 1
fi

if (( ! $suppress )) ; then
    echo "Job name   : $jobname"
    echo "Job status : $job_status"
    echo "Status dir : $status_dir"
    echo "Job script : ${!job_status}"
    if [ -e $output ] ; then
        echo "Job output : $output"
    fi
    echo "Build dir  : $build_dir"
    echo
fi

if [ ! -e $complete ] ; then
    if (( $wait )) ; then
        echo "Waiting for job to complete"
        while [ ! -e $complete ] ; do
            sleep 1
        done
    elif (( $follow )) ; then
        while [ ! -e $complete_dir/${jobname}.out ] ; do
            sleep 1
        done

        tail -f $complete_dir/${jobname}.out
    fi
fi

make_status=$build_dir/${jobname}.sta
make_errors=$build_dir/${jobname}.err
make_logs=$build_dir/${jobname}.log

if (( ! $suppress )) ; then
    if [ -e $make_status -o -e $make_errors -o -e $make_logs ] ; then
        echo "Build directory contains the following files:"

        if [ -e $make_status ] ; then
            echo "Make status: $(basename $make_status) (status returned was: $(cat $make_status| tr '\r\n' ' '))"
        fi

        if [ -e $make_errors ] ; then
            echo "Error msgs: $(basename $make_errors)"
        fi

        if [ -e $make_logs ] ; then
            echo "Output log : $(basename $make_logs)"
        fi
    else
        echo "No build files found in build directory"
    fi
fi

# Now print out the relevant files
if (( $job )) && [ -e ${!job_status} ] ; then
    (( $suppress )) || echo -e "\nJob file ${!job_status}:"
    cat ${!job_status}
fi

if (( $out )) && [ -e $output ] ; then
    (( $suppress )) || echo -e "\nJob output file $output:"
    cat $output
fi

if (( $status )) && [ -e  $make_status ] ; then
    (( $suppress )) || echo -e "\nMake status file $make_status:"
    cat $make_status
fi

if (( $errors )) && [ -e  $make_errors ] ; then
    (( $suppress )) || echo -e "\nMake errors file $make_errors:"
    cat $make_errors
fi

if (( $logs )) && [ -e  $make_logs ] ; then
    (( $suppress )) || echo -e "\nMake logs file $make_logs:"
    cat $make_logs
fi

