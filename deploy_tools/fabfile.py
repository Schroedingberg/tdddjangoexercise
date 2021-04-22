import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run


CONDA = True

REPO_URL = 'https://github.com/Schroedingberg/tdddjangoexercise.git'

conda_binary = f'/home/{env.user}/miniconda3/condabin/conda'

def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        print("Getting latest source....")
        _get_latest_source()
        print("OK")
        print("Updating venv....")
        _update_virtualenv()
        print("OK")
        print("Updating .env....")
        _create_or_update_dotenv()
        print("OK")
        print("Updating static files")
        _update_static_files()
        print("OK")
        print("Upgrading database....")
        _upgrade_database()
        print("OK")



def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local("git log -n 1 --format=%H", capture = True)
    run(f'git reset --hard {current_commit}')


def _update_virtualenv():
    if CONDA:
        #if not exists(f'/home/{env.user}/miniconda3/envs/old_django'):
            #run(f'{conda_binary} create --name old_django python=3.6')
        #run(f'{conda_binary} install --force-reinstall -y -q --name old_django  --file requirements.txt')
        pass # Since conda was only used for exercise purposes (pyvenv could not provide the required python executable) we are not going to do this step in a conda setting 
    else:
        if not exists('virtualenv/bin/pip'):
            run(f'python3.7 -m venv virtualenv')

        run('./virtualenv/bin/pip install -r requirements.txt')


def _create_or_update_dotenv( ):
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}' )
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices('abcdefghijklmnopqrstuvwxyz0123456789', k = 50))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')


def _update_static_files():
    if CONDA:
        run(f'/home/{env.user}/miniconda3/bin/python manage.py collectstatic --noinput')
    else:
        run('./virtualenv/bin/python manage.py collectstatic --noinput')


def _upgrade_database():
    if CONDA:
        run(f'/home/{env.user}/miniconda3/bin/python manage.py migrate --noinput')
    else:
        run('./virtualenv/bin/python manage.py migrate --noinput')
    
