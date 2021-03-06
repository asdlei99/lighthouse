from lighthouse.util.log import lmsg
from lighthouse.util.misc import iteritems
from lighthouse.util.disassembler import disassembler

#------------------------------------------------------------------------------
# Exception Definitions
#------------------------------------------------------------------------------

class LighthouseError(Exception):
    """
    An error generated by Lighthouse.
    """
    def __init__(self, *args, **kwargs):
        super(LighthouseError, self).__init__(*args, **kwargs)

#------------------------------------------------------------------------------
# Coverage File Exceptions
#------------------------------------------------------------------------------

class CoverageException(LighthouseError):
    """
    A class of errors pertaining to loading & mapping coverage files.
    """
    name = NotImplementedError
    description = NotImplementedError

    def __init__(self, message, filepath):
        super(CoverageException, self).__init__(message)
        self.filepath = filepath

    @property
    def verbose(self):
        return "Error: %s\n\n%s" % (self.name, self.description)

    def __str__(self):
        return self.message + " '%s'" % self.filepath

class CoverageParsingError(CoverageException):
    """
    An error generated by the CoverageReader when all parsers fail.
    """
    name = "PARSE_FAILURE"
    description = \
        "Failed to parse one or more of the selected coverage files!\n\n"  \
        " Possible reasons:\n"                                             \
        " - You selected a file that was *not* a coverage file.\n"         \
        " - The selected coverage file is malformed or unreadable.\n"      \
        " - A suitable parser for the coverage file is not installed.\n\n" \
        "Please see the disassembler console for more info..."

    def __init__(self, filepath, tracebacks):
        super(CoverageParsingError, self).__init__("Failed to parse coverage file", filepath)
        self.tracebacks = tracebacks

class CoverageMissingError(CoverageException):
    """
    An error generated when no data was extracted from a CoverageFile.
    """
    name = "NO_COVERAGE_ERROR"
    description = \
        "No usable coverage data was extracted from one of the selected files.\n\n" \
        " Possible reasons:\n"                                                      \
        " - You selected a coverage file for the wrong binary.\n"                   \
        " - The name of the executable file used to generate this database\n"       \
        "    is different than the one you collected coverage against.\n"           \
        " - Your DBI failed to collect any coverage for this binary.\n\n"           \
        "Please see the disassembler console for more info..."

    def __init__(self, filepath):
        super(CoverageMissingError, self).__init__("No coverage extracted from file", filepath)

class CoverageMappingAbsent(CoverageException):
    """
    A warning generated when coverage data cannot be mapped.
    """
    name = "NO_COVERAGE_MAPPED"
    description = \
        "One or more of the loaded coverage files has no visibly mapped data.\n\n" \
        " Possible reasons:\n"                                                     \
        " - The loaded coverage data does not fall within defined functions.\n"    \
        " - You loaded an absolute address trace with a different imagebase.\n"    \
        " - The coverage data might be corrupt or malformed.\n\n"                  \
        "Please see the disassembler console for more info..."

    def __init__(self, coverage):
        super(CoverageMappingAbsent, self).__init__("No coverage data could be mapped", coverage.filepath)
        self.coverage = coverage

class CoverageMappingSuspicious(CoverageException):
    """
    A warning generated when coverage data does not appear to match the database.
    """
    name = "BAD_COVERAGE_MAPPING"
    description = \
        "One or more of the loaded coverage files appears to be badly mapped.\n\n" \
        " Possible reasons:\n"                                                     \
        " - You selected the wrong binary/module to load coverage from.\n"         \
        " - Your coverage file/data is for a different version of the\n"           \
        "   binary that does not match what the disassembler has open.\n"          \
        " - You recorded self-modifying code or something with very\n"             \
        "    abnormal control flow (obfuscated code, malware, packers).\n"         \
        " - The coverage data might be corrupt or malformed.\n\n"                  \
        "This means that any coverage displayed by Lighthouse is PROBABLY\n"       \
        "WRONG and is not be trusted because the coverage data does not\n"         \
        "appear to match the disassembled binary."

    def __init__(self, coverage):
        super(CoverageMappingSuspicious, self).__init__("Coverage data appears badly mapped", coverage.filepath)
        self.coverage = coverage

#------------------------------------------------------------------------------
# UI Warnings
#------------------------------------------------------------------------------

def warn_errors(errors, ignore=[]):
    """
    Warn the user of any encountered errors with a messagebox.
    """
    if not errors:
        return

    for error_type, error_list in iteritems(errors):

        #
        # loop through the individual instances/files that caused this error
        # and dump the results to the disassembler console...
        #

        lmsg("-"*50)
        lmsg("Files reporting %s:" % error_type.name)
        for error in error_list:
            lmsg(" - %s" % error.filepath)

        # suppress popups for certain errors, if the user has specified such
        if error_type in ignore:
            continue

        #
        # popup a more verbose error messagebox for the user to read regarding
        # this class of error they encountered
        #

        disassembler.warning(error.verbose)

    # done ...
    lmsg("-"*50)
