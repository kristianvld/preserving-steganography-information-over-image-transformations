from methods.method import Method
from transformations.transformation import Transformation
from transformations.none_transform import NoneTransformation
from PIL import Image
from utils.logger import print, debug, path
from utils import logger
from ansi.color import fg
import os
import shutil
import argparse
from utils import stats

def mkdirs(path: str):
    if not os.path.isdir(path):
        os.mkdir(path)
    
def subsection_ignore_case(obj_type, objects, section):
    if not section:
        return objects

    out = []
    names = [el if type(el) == str else el.__name__ for el in objects]
    for el in section.split(','):
        index = -1
        for i, name in enumerate(names):
            if el.lower() in name.lower():
                out.append(objects[i])
                index = i
        if index == -1:
            print('Unknown', obj_type, repr(el))
            print('Valid options:', names)
            exit(1)
        
    return out

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--methods', help="Comma seperated list of methods to test")
    parser.add_argument('--transforms', help="Comma seperated list of transformations to test")
    parser.add_argument('--samples', help="Comma seperated list of images to test")
    parser.add_argument('--messages', nargs='+', help="List of messages. Can be specified multiple times")
    parser.add_argument('--list', action="store_const", const=True, help="List methods, transformations and samples without running tests.")
    parser.add_argument('--verbose', action="store_const", const=True, help="Show verbose output")
    parser.add_argument('--original', action="store_const", const=True, help="Apply original steganography method no matter what transformations are applied after.")
    parser.add_argument('--latex', action="store_const", const=True, help="Generate latex tables")
    parser.add_argument('--no-skip', action="store_const", const=True, help="Do not skip any tests.")

    args = parser.parse_args()

    logger.log_debug = args.verbose

    methods = Method.__subclasses__()
    methods = subsection_ignore_case('method', methods, args.methods)
    print('Methods:', [m.__name__ for m in methods])

    transformations = Transformation.__subclasses__()
    transformations = subsection_ignore_case('transformation', transformations, args.transforms)
    print('Transformations:', [t.__name__ for t in transformations])

    messages = [b'Attack at Dawn']
    messages = [msg.encode() for msg in args.messages] if args.messages else messages
    print('Messages:', messages)

    samples = [f for f in os.listdir('samples') if os.path.isfile('samples/' + f)]
    samples = subsection_ignore_case('sample', samples, args.samples)
    print('Samples:', samples)

    if args.list:
        exit()

    mkdirs('outputs')
    shutil.rmtree('outputs')
    mkdirs('outputs')
    print()

    fails = []
    success = []
    errors = []
    _stats = []
    for method in methods:
        method_name = method.__name__
        method: Method = method()
        for transformation in transformations:
            transformation_name = transformation.__name__ 
            transformation: Transformation = transformation()
            stego_transformation = NoneTransformation() if args.original else transformation
            
            for sample in samples:
                src = f'samples/{sample}'
                src = shutil.copy(src, f'outputs/orig-{sample}')

                if '2png' in transformation_name.lower() and src.lower().endswith('.png') and not args.no_skip:
                    print('Source is PNG image and transformation is convert to PNG, skippping...')
                    continue
                if '2jpg' in transformation_name.lower() and src.lower().endswith('.jpg') or src.lower().endswith('.jpeg') and not args.no_skip:
                    print('Source is JPEG image and transformation is convert to JPEG, skipping...')
                    continue

                for i, message in enumerate(messages):
                    entry = f'{method_name}-{transformation_name}-MSG-{i}-{sample}'
                    
                    print('='*80)
                    print('Sample:', sample)
                    print('Message:', message)
                    print()
                    print(f'Applying method {method_name}-{transformation_name}')
                    dst_pre =  f'outputs/pre-{transformation_name}-{method_name}-MSG-{i}-{sample}'
                    try:
                        method.apply(message, src, dst_pre, stego_transformation)
                        print('Saved to:', *path(dst_pre))
                        print()

                        dst_transformed = f'outputs/transformed-{method_name}-{transformation_name}-MSG-{i}-{sample}'
                        print(f'Applying transformation: {transformation_name}')
                        dst_transformed = transformation.apply(dst_pre, dst_transformed)
                        print('Saved to:', *path(dst_transformed))
                        print()

                        extracted = method.extract(dst_transformed, stego_transformation)
                        print('Extracted:', extracted if args.verbose else extracted[:50], len(extracted))
                        print('Able to extract message:', message in extracted)
                        print()

                        dst_transformed_only = f'outputs/transformed-{transformation_name}-{sample}'
                        dst_transformed_only = transformation.apply(src, dst_transformed_only)
                        print('Diff between:', *path(dst_transformed), 'and', *path(dst_transformed_only))
                        img_src = Image.open(dst_transformed_only)
                        img_dst = Image.open(dst_transformed)

                        mse = stats.mse(img_src, img_dst)
                        psnr = stats.psnr(img_src, img_dst)
                        ncc = stats.ncc(img_src, img_dst)
                        print('MSE:', mse)
                        print('PSNR:', psnr)
                        print('NCC:', ncc)
                        print()

                        dst_diff = f'outputs/diff-{method_name}-{transformation_name}-MSG-{i}-{sample}'
                        img_diff, amplify = stats.diff(img_src, img_dst)
                        img_diff.save(dst_diff, quality='maximum')
                        print('Diff saved to:', *path(dst_diff))
                        print('Diff amplification:', amplify)



                        if message in extracted:
                            success.append(entry)
                        else:
                            fails.append(entry)
                        
                        _stats.append({
                            'name': sample,
                            'mse': mse,
                            'psnr': psnr,
                            'ncc': ncc,
                        })

                    except NotImplementedError as e:
                        print(fg.red, '[ERROR] ' + e.args[0])
                        errors.append(entry)

                    print('='*80)
                    print()


    print('Errors:', fg.red, len(errors))
    for error in errors:
        print(' - ', fg.red, error, sep='')
    print('Fails:', fg.red, len(fails))
    for fail in fails:
        print(' - ', fg.red, fail, sep='')
    print('Success:', fg.green, len(success))
    for suc in success:
        print(' - ', fg.green, suc, sep='')
    
    if args.latex:
        def entry(sample):
            if len(sample) == 0:
                return sample
            sample = sample.split('-')
            sample = sample[1] + '-' + sample[4]
            return sample.replace('_', '\\_')
        
        results = sorted(_stats, key=lambda e: ''.join(e['name'].split('.')[::-1]))
        mean = {k: sum(e[k] for e in results) / len(results) for k in ['mse', 'psnr', 'ncc']}
        decimals = '.10f'

        print('\\begin{table}[]')
        print('\t\\centering')
        print('\t\\begin{tabular}{|l|r|r|r|r|}')
        print('\t\\hline')
        print('\t\t', '\\textbf{Category}', '&', '\\textbf{MSE}', '&', '\\textbf{PSNR}', '&', '\\textbf{NCC}', '&', '\\textbf{Sample Size}', '\\\\')
        print('\t\\hline')
        print('\t\t', f'{args.samples}-{args.transforms}', ' & '.join([n if type(n) == str else f'{n:{decimals}}' for n in mean.values()]), '&', len(results), '\\\\')
        print('\t\\hline')
        print('\t\\end{tabular}')
        print('\t\\caption{XXX}')
        print('\t\\label{tab:XXX}')
        print('\\end{table}')
        print()

        print('\\begin{table}[]')
        print('\t\\centering')
        print('\t\\begin{tabular}{|l|l|r|r|}')
        print('\t\\hline')
        print('\t\t', '\\textbf{Transformation}', '&', '\\textbf{Category}', '&', '\\textbf{Success rate}', '&', '\\textbf{Sample Size}', '\\\\')
        print('\t\\hline')
        print('\t\t', f'{args.samples}-{args.transforms}', '&', 'XXXX', '&', f'{len(success) * 100 / (len(success) + len(fails)):.1f}\\%', '&', len(success) + len(fails), '\\\\')
        print('\t\\hline')
        print('\t\\end{tabular}')
        print('\t\\caption{Success rate of %s with %s.}' % (f'{args.samples}-{args.transforms}', args.methods))
        print('\t\\label{tab:XXX}')
        print('\\end{table}')
        