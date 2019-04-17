"""
Calculate the times of a given phase for a series of objects with
a given set of ephemerides

Input file must have the following format:

target_id  epoch  period  t14

The output will be in the following format:

   1. A per target list containing chronological times of
      the requested phases
   1. A combined list of all target's phases in chronological order

"""
import argparse as ap
from collections import defaultdict
from datetime import (
    datetime,
    timedelta
    )
from astropy.time import Time
from astropy.coordinates import (
    EarthLocation,
    get_sun,
    AltAz
    )

def arg_parse():
    """
    parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('infile',
                   help='path to file containing objects')
    p.add_argument('n1',
                   help='night 1')
    p.add_argument('n2',
                   help='night 2')
    p.add_argument('observatory',
                   help='Astropy name of observatory')
    return p.parse_args()

def read_ephem_file(infile):
    """
    read in the ephem file and split up the info
    """
    target_id, epoch, period, tdur = [], [], [], []
    with open(infile) as ff:
        data = ff.readlines()
    for row in data:
        s = row.split()
        target_id.append(s[0])
        epoch.append(float(s[1]))
        period.append(float(s[2]))
        tdur.append(float(s[3]))
    return target_id, epoch, period, tdur

def sun_is_down(check_time, observatory):
    """
    return True or False whether the sun is below -14 deg altitude
    """
    sun = get_sun(check_time).transform_to(AltAz(obstime=check_time, location=observatory))
    return sun.alt.value < -14

if __name__ == "__main__":
    args = arg_parse()
    # observatory location
    observatory = EarthLocation.of_site(args.observatory)
    # read in the ephem file
    target_ids, epochs, periods, tdurs = read_ephem_file(args.infile)
    # get times for the observing run
    n1 = datetime.strptime(args.n1, '%Y-%m-%d') + timedelta(hours=12)
    # add 1 extra day so the n's are nights of
    n2 = datetime.strptime(args.n2, '%Y-%m-%d') + timedelta(hours=36)
    n1_T = Time(n1, format='datetime', scale='utc', location=observatory)
    n2_T = Time(n2, format='datetime', scale='utc', location=observatory)
    # loop over each target
    q1_epochs = defaultdict(list)
    q2_epochs = defaultdict(list)
    chron = {}
    for target_id, epoch, period, tdur in zip(target_ids, epochs, periods, tdurs):
        print("Target: {}".format(target_id))
        # find the starting point
        epoch_start = 0
        i = 0
        while epoch_start < n1_T.jd:
            epoch_start = epoch + i*period
            i += 1
        # step back 1 period
        epoch_start = epoch_start - period
        # now loop over the range and pull out which epochs are useable
        i = 0
        current_epoch = epoch_start
        while current_epoch < n2_T.jd:
            q1 = epoch_start + i*period + (0.25*period)
            q1_T = Time(q1, format='jd', scale='utc')
            q2 = epoch_start + i*period - (0.25*period)
            q2_T = Time(q2, format='jd', scale='utc')
            if q1 >= n1_T.jd and q1 <= n2_T.jd:
                # check for sun elevation
                if sun_is_down(q1_T, observatory):
                    q1_epochs[target_id].append(q1_T)
                    chron[q1_T.jd] = "{}  {}  q1".format(q1_T.datetime, target_id)
                    print("\t{} q1".format(q1_T.datetime))
            if q2 >= n1_T.jd and q2 <= n2_T.jd:
                if sun_is_down(q2_T, observatory):
                    q2_epochs[target_id].append(q2_T)
                    chron[q2_T.jd] = "{}  {}  q2".format(q2_T.datetime, target_id)
                    print("\t{} q2".format(q2_T.datetime))
            i += 1
            current_epoch = epoch_start + i*period

    print("\nChronological summary:")
    # print a chronological summary
    for item in sorted(chron.keys()):
        print("\t{}".format(chron[item]))

