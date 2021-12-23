from maya import cmds
import maya.mel as mel
import sys, os


def batchExport(sourcePath, destPath, toFileType='fbx', recursively=True, matchDirectorySructure=True, **keywords):
    """
	Batch export files in one location to another location. Returns True on
	success. Only intended for use in standalone mode; otherwise FBX settings
	are not respected. Not all FBX Export settings are currently supported. Not
	all versions of Maya have been completely tested; please tell me if you
	find errors in old versions.
	@param filePatterns List corresponding to different file extensions to parse
	@param filterPrefix List corresponding to required prefixes in file names
	@param filterSuffix List corresponding to required suffixes in file names
	@param filterContains List corresponding to required string in file names
	@param addPrefix String to prefix on all exported files
	@param addSuffix String to suffix on all exported files
	@param bakeAll String specifying object types on which to bake animation
	@param bakeAllRange Tuple or list specifying a frame range
	@param maVersion Version of Maya to set for .ma exports
	@param fbxVersion FBXFileVersion string
	@param fbxAscii FBXExportInAscii
	@param fbxBake FBXExportBakeComplexAnimation boolean
	@param fbxBakeStart FBXExportBakeComplexStart float
	@param fbxBakeEnd FBXExportBakeComplexEnd
	@param fbxAnimOnly FBXExportAnimationOnly boolean
	@param fbxConstraints FBXExportConstraints boolean
	@param fbxUnit FBXConvertUnitString and FBXExportConvertUnitString
	@param fbxUpAxis FBXExportUpAxis
	@param fbxAxisConvert FBXExportAxisConversionMethod
	@param fbxScale FBXExportScaleFactor
	"""
    # make sure that the file type string comes in as expected
    try:
        toFileType = toFileType.lower()
        toFileType = toFileType[toFileType.rfind('.') + 1:len(toFileType)]
    except:
        raise

    if toFileType == 'fbx':
        # early out if the plug-in has not been loaded
        try:
            cmds.FBXExport
        except:
            try:
                cmds.loadPlugin('fbxmaya')
            except:
                sys.stderr.write('ERROR: FBX Export Plug-in was not detected.\n')
                return False
        # configure FBX export settings
        try:
            mel.eval('FBXExportFileVersion %s' % keywords[
                'fbxVersion'])  # absent before Maya 2009, but should simply print a benign error message
        except:
            pass
        try:
            mel.eval('FBXExportAscii %s' % keywords['fbxAscii'].__str__().lower())
        except:
            pass
        try:
            mel.eval('FBXExportBakeComplexAnimation -v %s' % keywords['fbxBake'].__str__().lower())
            try:
                mel.eval('FBXExportBakeComplexStart -v %s' % keywords['fbxBakeStart'])
            except:
                mel.eval('FBXExportBakeComplexStart -v %i' % math.floor(cmds.playbackOptions(q=True, min=True)))
            try:
                mel.eval('FBXExportBakeComplexEnd -v %s' % keywords['fbxBakeEnd'])
            except:
                mel.eval('FBXExportBakeComplexEnd -v %i' % math.ceil(cmds.playbackOptions(q=True, max=True)))
        except:
            pass
        try:
            mel.eval('FBXExportAnimationOnly -v %s' % keywords['fbxAnimOnly'].__str__().lower())
        except:
            pass
        try:
            mel.eval('FBXExportConstraints -v %s' % keywords['fbxConstraints'].__str__().lower())
        except:
            pass
        try:
            mel.eval('FBXExportConvertUnitString -v %s' % keywords['fbxUnit'])
        except:
            try:
                mel.eval('FBXConvertUnitString -v %s' % keywords['fbxUnit'])
            except:
                pass
        try:
            mel.eval('FBXExportUpAxis -v %s' % keywords['fbxUpAxis'])
        except:
            pass
        try:
            mel.eval('FBXExportAxisConversionMethod -v %s' % keywords['fbxAxisConvert'])
        except:
            pass
        try:
            mel.eval('FBXExportScaleFactor -v %s' % keywords['fbxScale'])
        except:
            pass
    elif toFileType == 'ma':
        try:
            maVersion = keywords['maVersion']
            maVersion = convertValidTypesToStringList(maVersion, [types.StringTypes, types.IntType, types.FloatType])
            maVersion = maVersion[0]
        except:
            maVersion = None
    else:
        sys.stderr.write('ERROR: %s is not a supported file type.\n' % toFileType)
        return False

    # parse the keywords
    try:
        filePatterns = keywords['filePatterns']
    except:
        filePatterns = ['mb', 'ma']
    try:
        filterPrefix = keywords['filterPrefix']
    except:
        filterPrefix = ['']
    try:
        filterSuffix = keywords['filterSuffix']
    except:
        filterSuffix = ['']
    try:
        filterContains = keywords['filterContains']
    except:
        filterContains = ['']
    try:
        addPrefix = '%s' % keywords['addPrefix']
    except:
        addPrefix = ''
    try:
        addSuffix = '%s' % keywords['addSuffix']
    except:
        addSuffix = ''
    try:
        bakeAll = keywords['bakeAll']
        if not isinstance(bakeAll, types.StringTypes):
            sys.stderr.write(
                "WARNING: Invalid argument %s specified for bakeAll. Type 'dag' is being used instead.\n" % bakeAll)
            bakeAll = 'dag'
    except:
        bakeAll = None
    try:
        bakeAllRange = keywords['bakeAllRange']
        if not type(bakeAllRange) == types.ListType or not type(bakeAllRange) == types.TupleType or not len(
                bakeAllRange) == 2:
            sys.stderr.write(
                'WARNING: Invalid argument %s specified for bakeAllRange. Timeline is being used instead.\n' % bakeAllRange)
            bakeAllRange = None
    except:
        bakeAllRange = None

    # create the destination folders
    if matchDirectorySructure:
        if copyDirectoryStructure(sourcePath, destPath, False) == False: return False
    else:
        try:
            os.listdir(destPath)
        except:
            try:
                os.makedirs(destPath)
            except:
                return False

    # get a list of all of the source files
    files = find(sourcePath, recursively, False, paths='relative', filePatterns=filePatterns, filterPrefix=filterPrefix,
                 filterSuffix=filterSuffix, filterContains=filterContains)

    # export an fbx for each file
    for file in files:
        # build the export path and filename
        relativeLocation = ''
        filename = file[0:file.rfind('.')]
        if file.rfind('/') > -1:
            if matchDirectorySructure: relativeLocation = file[0:file.rfind('/') + 1]
            filename = file[file.rfind('/') + 1:file.rfind('.')]
        exportAsString = '%s/%s%s%s%s.%s' % (destPath, relativeLocation, addPrefix, filename, addSuffix, toFileType)
        try:
            # open the source file
            cmds.file('%s/%s' % (sourcePath, file), o=True, force=True)
            # export to the proper location
            try:
                if bakeAll:
                    try:
                        if not bakeAllRange:
                            cmds.bakeResults(cmds.ls(type=bakeAll), sm=True, time=(
                            math.floor(cmds.playbackOptions(q=True, min=True)),
                            math.ceil(cmds.playbackOptions(q=True, max=True))))
                        else:
                            cmds.bakeResults(cmds.ls(type=bakeAll), sm=True, time=bakeAllRange)
                    except:
                        sys.stderr.write('WARNING: Unable to bake objects of type %s in file %s.\n' % (bakeAll, file))
                    try:
                        for object in cmds.ls(type=bakeAll):
                            amTools.utilities.animation.smoothAnimCurves(object, False)
                    except:
                        sys.stderr.write(
                            'WARNING: Unable to correct tangents on baked objects of type %s in file %s.\n' % (
                            bakeAll, file))
                if toFileType == 'fbx':
                    mel.eval('FBXExport -f "%s";' % exportAsString)  # TODO: failing on patched .ma files
                elif toFileType == 'ma':
                    cmds.file(exportAsString, ea=True, type='mayaAscii', force=True)
                    patchMayaAsciiFile(exportAsString, maVersion)
            except:
                sys.stderr.write('WARNING: Unable to export the file %s. It is being skipped.\n' % file[file.rfind(
                    '/') + 1:len(file)])
        except:
            sys.stderr.write(
                'WARNING: Unable to read the file %s. It is being skipped.\n' % file[file.rfind('/') + 1:len(file)])

    return True
